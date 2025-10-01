"""
Langfuse Integration Module for OMD Enhanced Research Agent

This module provides a clean interface for integrating Langfuse observability
into the Enhanced Research Agent, with support for tracing LLM calls, agent steps,
and MCP server interactions.
"""

import os
import functools
from typing import Optional, Dict, Any, Callable
from contextlib import contextmanager
import asyncio
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Try to import Langfuse
try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    Langfuse = None  # Type hint placeholder
    print("⚠️  Langfuse not installed. Observability features disabled.")


class LangfuseManager:
    """
    Manager class for Langfuse integration.
    Provides centralized access to Langfuse client and tracing utilities.
    """
    
    _instance = None
    _client: Optional[Langfuse] = None
    _enabled: bool = False
    _current_session_id: Optional[str] = None
    _current_user_id: Optional[str] = None
    
    def __new__(cls):
        """Singleton pattern to ensure one client instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the Langfuse client."""
        if not LANGFUSE_AVAILABLE:
            print("⚠️  Langfuse not available")
            return
        
        # Check if enabled
        enabled_str = os.getenv('LANGFUSE_ENABLED', 'true').lower()
        self._enabled = enabled_str in ('true', '1', 'yes')
        
        if not self._enabled:
            print("ℹ️  Langfuse disabled via configuration")
            return
        
        try:
            public_key = os.getenv('LANGFUSE_PUBLIC_KEY')
            secret_key = os.getenv('LANGFUSE_SECRET_KEY')
            host = os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')
            
            if not public_key or not secret_key:
                print("⚠️  Langfuse keys not configured. Tracing disabled.")
                self._enabled = False
                return
            
            self._client = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=host,
                debug=os.getenv('DEBUG', 'false').lower() == 'true',
                flush_at=int(os.getenv('LANGFUSE_FLUSH_AT', '15')),
                flush_interval=float(os.getenv('LANGFUSE_FLUSH_INTERVAL', '0.5')),
            )
            
            print(f"✅ Langfuse initialized: {host}")
            
        except Exception as e:
            print(f"❌ Failed to initialize Langfuse: {e}")
            self._enabled = False
            self._client = None
    
    @property
    def client(self) -> Optional[Langfuse]:
        """Get the Langfuse client instance."""
        return self._client
    
    @property
    def enabled(self) -> bool:
        """Check if Langfuse tracing is enabled."""
        return self._enabled and self._client is not None
    
    @property
    def current_session_id(self) -> Optional[str]:
        """Get the current session ID."""
        return self._current_session_id
    
    @property
    def current_user_id(self) -> Optional[str]:
        """Get the current user ID."""
        return self._current_user_id
    
    def set_session(self, session_id: str, user_id: Optional[str] = None):
        """
        Set the current session ID for grouping traces.
        
        Args:
            session_id: Unique identifier for this session
            user_id: Optional user identifier
        
        Usage:
            langfuse_manager.set_session("session-123", user_id="user-456")
        
        Note:
            Session info is stored and will be automatically added to all future
            trace spans. No need to have an active trace when calling this.
        """
        self._current_session_id = session_id
        if user_id:
            self._current_user_id = user_id
    
    def set_user(self, user_id: str):
        """
        Set the current user ID.
        
        Args:
            user_id: Unique identifier for the user
        
        Note:
            User info is stored and will be automatically added to all future
            trace spans. No need to have an active trace when calling this.
        """
        self._current_user_id = user_id
    
    def clear_session(self):
        """Clear the current session ID."""
        self._current_session_id = None
        self._current_user_id = None
    
    def shutdown(self):
        """Shutdown and flush remaining events."""
        if self._client:
            self._client.flush()
            self._client.shutdown()
    
    @contextmanager
    def trace_span(self, name: str, **kwargs):
        """
        Context manager for creating a traced span.
        
        Usage:
            with langfuse_manager.trace_span("my_operation", metadata={"key": "value"}):
                # do work
                pass
        """
        if not self.enabled:
            yield None
            return
        
        try:
            with self._client.start_as_current_span(name=name) as span:
                # Automatically add session and user info to trace
                trace_updates = {}
                if self._current_session_id:
                    trace_updates["session_id"] = self._current_session_id
                if self._current_user_id:
                    trace_updates["user_id"] = self._current_user_id
                
                if trace_updates and span:
                    try:
                        span.update_trace(**trace_updates)
                    except Exception:
                        # Silently ignore if no active trace
                        pass
                
                # Add any additional kwargs
                if kwargs:
                    span.update(**kwargs)
                
                yield span
        except Exception as e:
            print(f"⚠️  Langfuse span error: {e}")
            yield None
    
    def trace_llm_call(self, 
                       model: str,
                       input_text: str,
                       output_text: str,
                       metadata: Optional[Dict[str, Any]] = None,
                       usage: Optional[Dict[str, int]] = None):
        """
        Manually trace an LLM call.
        
        Args:
            model: Model name (e.g., "gpt-3.5-turbo")
            input_text: Input prompt
            output_text: Model response
            metadata: Additional metadata
            usage: Token usage dict with 'prompt_tokens', 'completion_tokens', 'total_tokens'
        """
        if not self.enabled:
            return
        
        try:
            # Create a generation observation
            generation = self._client.start_observation(
                name=f"llm_call_{model}",
                as_type="generation",
                model=model,
                input=input_text,
                metadata=metadata or {}
            )
            
            # Update with output and usage
            generation.update(
                output=output_text,
                usage=usage
            )
            
            # End the observation
            generation.end()
        except Exception as e:
            print(f"⚠️  Error tracing LLM call: {e}")
    
    def trace_agent_step(self,
                        step_type: str,
                        input_data: Any,
                        output_data: Any,
                        metadata: Optional[Dict[str, Any]] = None):
        """
        Trace an agent reasoning step.
        
        Args:
            step_type: Type of step (e.g., "think", "act", "observe")
            input_data: Input to the step
            output_data: Output from the step
            metadata: Additional metadata
        """
        if not self.enabled:
            return
        
        try:
            with self._client.start_as_current_span(
                name=f"agent_step_{step_type}"
            ) as span:
                # Add session info to trace
                if self._current_session_id:
                    span.update_trace(session_id=self._current_session_id)
                if self._current_user_id:
                    span.update_trace(user_id=self._current_user_id)
                
                span.update(
                    input=str(input_data),
                    output=str(output_data),
                    metadata=metadata or {},
                    tags=["agent", step_type]
                )
        except Exception as e:
            print(f"⚠️  Error tracing agent step: {e}")
    
    def trace_mcp_call(self,
                      server_name: str,
                      query: str,
                      response: str,
                      latency_ms: Optional[float] = None,
                      metadata: Optional[Dict[str, Any]] = None):
        """
        Trace an MCP server call.
        
        Args:
            server_name: Name of the MCP server
            query: Query sent to server
            response: Response from server
            latency_ms: Response latency in milliseconds
            metadata: Additional metadata
        """
        if not self.enabled:
            return
        
        try:
            meta = metadata or {}
            if latency_ms:
                meta['latency_ms'] = latency_ms
            meta['server'] = server_name
            
            with self._client.start_as_current_span(
                name=f"mcp_call_{server_name}"
            ) as span:
                # Add session info to trace
                if self._current_session_id:
                    span.update_trace(session_id=self._current_session_id)
                if self._current_user_id:
                    span.update_trace(user_id=self._current_user_id)
                
                span.update(
                    input=query,
                    output=response,
                    metadata=meta,
                    tags=["mcp", server_name]
                )
        except Exception as e:
            print(f"⚠️  Error tracing MCP call: {e}")
    
    def update_current_trace(self, **kwargs):
        """Update the current trace with additional information."""
        if not self.enabled:
            return
        
        try:
            self._client.update_current_trace(**kwargs)
        except Exception as e:
            print(f"⚠️  Error updating trace: {e}")
    
    def score_current_trace(self, name: str, value: float, comment: Optional[str] = None):
        """
        Add a score to the current trace.
        
        Args:
            name: Score name (e.g., "user_feedback", "quality")
            value: Score value
            comment: Optional comment
        """
        if not self.enabled:
            return
        
        try:
            self._client.score_current_trace(
                name=name,
                value=value,
                comment=comment
            )
        except Exception as e:
            print(f"⚠️  Error scoring trace: {e}")


# Global instance
langfuse_manager = LangfuseManager()


# Decorator for tracing functions
def trace_function(name: Optional[str] = None, **trace_kwargs):
    """
    Decorator to automatically trace a function.
    
    Usage:
        @trace_function(name="my_function", metadata={"version": "1.0"})
        def my_function(arg1, arg2):
            return arg1 + arg2
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not langfuse_manager.enabled:
                return func(*args, **kwargs)
            
            func_name = name or func.__name__
            with langfuse_manager.trace_span(func_name, **trace_kwargs):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def trace_async_function(name: Optional[str] = None, **trace_kwargs):
    """
    Decorator to automatically trace an async function.
    
    Usage:
        @trace_async_function(name="my_async_function")
        async def my_async_function(arg1):
            return await some_async_operation(arg1)
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not langfuse_manager.enabled:
                return await func(*args, **kwargs)
            
            func_name = name or func.__name__
            with langfuse_manager.trace_span(func_name, **trace_kwargs):
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Cleanup function
def shutdown_langfuse():
    """Shutdown Langfuse and flush remaining events."""
    langfuse_manager.shutdown()


if __name__ == "__main__":
    # Test the integration
    print("Testing Langfuse Integration\n")
    print(f"Langfuse available: {LANGFUSE_AVAILABLE}")
    print(f"Langfuse enabled: {langfuse_manager.enabled}")
    
    if langfuse_manager.enabled:
        print("\nTesting trace span...")
        with langfuse_manager.trace_span("test_operation", metadata={"test": True}):
            print("Inside traced span")
        
        print("✅ Integration test complete")
        shutdown_langfuse()
    else:
        print("\n⚠️  Langfuse not enabled. Check configuration.")
