import asyncio
from typing import Optional
from pathlib import Path
import os

# Load environment variables from .env file (if available)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not available, using environment variables only")
    # Define a dummy load_dotenv function to prevent errors
    def load_dotenv():
        pass

# Import our integration modules
from .dspy_mcp_integration import DSPyMCPIntegration
from .mcp_client import MCPClient

# Import OpenManus components
from openmanus.agent import ReActAgent
from openmanus.config import Config
from openmanus.schema import Message, AgentState

# Import privacy features
try:
    from privacy import get_redacted_logger, get_session_manager
    logger = get_redacted_logger(__name__)
    session_manager = get_session_manager()
except ImportError:
    import logging
    # Create a compatibility wrapper that mimics RedactedLogger interface
    class _LoggerWrapper:
        def __init__(self, logger):
            self._logger = logger
        
        def info_user_input(self, message: str, user_input: str):
            """Fallback for info_user_input when privacy module unavailable"""
            self._logger.info(f"{message}: {user_input[:100]}..." if len(user_input) > 100 else f"{message}: {user_input}")
        
        def info_agent_output(self, message: str, agent_output: str):
            """Fallback for info_agent_output when privacy module unavailable"""
            self._logger.info(f"{message}: {agent_output[:100]}..." if len(agent_output) > 100 else f"{message}: {agent_output}")
        
        # Proxy standard logging methods
        def debug(self, *args, **kwargs):
            self._logger.debug(*args, **kwargs)
        
        def info(self, *args, **kwargs):
            self._logger.info(*args, **kwargs)
        
        def warning(self, *args, **kwargs):
            self._logger.warning(*args, **kwargs)
        
        def error(self, *args, **kwargs):
            self._logger.error(*args, **kwargs)
        
        def critical(self, *args, **kwargs):
            self._logger.critical(*args, **kwargs)
    
    logger = _LoggerWrapper(logging.getLogger(__name__))
    session_manager = None

# Configure OpenManus - Config is a singleton that auto-loads
config = Config()

# Import configuration helper
from .config_helper import get_model_config, is_cloud_environment, get_llm_provider_config

# Get appropriate model for current environment
provider_config = get_llm_provider_config()
model_name = provider_config["model"]
environment = "cloud" if is_cloud_environment() else "local"
print(f"🌍 Environment: {environment}")
print(f"🤖 Using LLM provider: {provider_config['provider']}")
print(f"🤖 Using model: {model_name}")

# Check if we have a valid provider
if provider_config["provider"] == "none":
    print("❌ CRITICAL: No LLM provider configured!")
    print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in Railway environment variables.")
    dspy_mcp = None
    mcp_client = None
else:
    # #region agent log
    import json
    import time as _time
    log_path = '/Users/raymondhunter/LocalProjects/10workspaceOct25/omd/.cursor/debug.log'
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({'sessionId': 'debug-session', 'runId': 'run2', 'hypothesisId': 'B', 'location': 'app.py:71-74', 'message': 'Model selection at startup (FIXED)', 'data': {'model_name': model_name, 'environment': environment, 'provider': provider_config['provider'], 'OPENAI_API_KEY': bool(os.getenv('OPENAI_API_KEY')), 'ANTHROPIC_API_KEY': bool(os.getenv('ANTHROPIC_API_KEY')), 'RAILWAY_ENVIRONMENT': os.getenv('RAILWAY_ENVIRONMENT')}, 'timestamp': _time.time() * 1000}) + '\n')
    except: pass
    # #endregion

# Initialize DSPy+MCP integration
if provider_config["provider"] != "none":
    try:
        dspy_mcp = DSPyMCPIntegration(
            llm_model=model_name,
            dspy_cache=True
        )
        print("✅ DSPy+MCP integration initialized successfully")
        # #region agent log
        import json
        log_path = '/Users/raymondhunter/LocalProjects/10workspaceOct25/omd/.cursor/debug.log'
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({'sessionId': 'debug-session', 'runId': 'run2', 'hypothesisId': 'C', 'location': 'app.py:78-82', 'message': 'DSPy+MCP initialization SUCCESS (FIXED)', 'data': {'model_name': model_name, 'provider': provider_config['provider']}, 'timestamp': _time.time() * 1000}) + '\n')
        except: pass
        # #endregion
    except Exception as e:
        print(f"⚠️  Warning: DSPy+MCP integration failed to initialize: {e}")
        print("📝 Falling back to basic MCP client")
        # #region agent log
        import json
        log_path = '/Users/raymondhunter/LocalProjects/10workspaceOct25/omd/.cursor/debug.log'
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps({'sessionId': 'debug-session', 'runId': 'run2', 'hypothesisId': 'E', 'location': 'app.py:84-87', 'message': 'DSPy+MCP initialization FAILED, using fallback', 'data': {'model_name': model_name, 'error': str(e), 'error_type': type(e).__name__}, 'timestamp': _time.time() * 1000}) + '\n')
        except: pass
        # #endregion
        dspy_mcp = None
        mcp_client = MCPClient()


class EnhancedResearchAgent(ReActAgent):
    """
    An agent that combines OpenManus ReAct pattern with DSPy structured reasoning 
    and MCP information gathering for enhanced research capabilities.
    
    Supports session-scoped conversation history when session_manager is available.
    """
    
    def __init__(self, name: str, description: Optional[str] = None, session_id: Optional[str] = None):
        super().__init__(name=name, description=description)
        
        # Choose integration mode based on availability
        self.use_dspy_integration = dspy_mcp is not None
        
        if self.use_dspy_integration:
            self.dspy_mcp = dspy_mcp
            print("🧠 Agent using DSPy+MCP structured reasoning")
        else:
            self.mcp_client = MCPClient()
            print("📝 Agent using basic MCP client (DSPy unavailable)")
        
        # Session-aware state management
        self.session_id = session_id
        self.use_session_isolation = session_manager is not None and session_id is not None
        
        if self.use_session_isolation:
            logger.info(f"Agent initialized with session isolation: {session_id}")
        
        # State management
        self.current_query = None
        self.research_result = None
        self.processing_step = None
    
    def update_memory(self, role: str, content: str):
        """Override to add session-scoped memory storage"""
        # Call parent method to maintain OpenManus memory
        super().update_memory(role, content)
        
        # Also store in session-scoped history if available
        if self.use_session_isolation:
            session_manager.add_message(
                session_id=self.session_id,
                role=role,
                content=content
            )
    
    def get_session_history(self):
        """Get conversation history for the current session"""
        if self.use_session_isolation:
            return session_manager.get_history(self.session_id)
        return self.memory.messages if hasattr(self, 'memory') else []
        
    async def think(self) -> bool:
        """Enhanced thinking process using DSPy structured reasoning when available"""
        # Get the last user message
        last_user_msg = next((msg for msg in reversed(self.memory.messages) 
                            if msg.role == "user"), None)
        
        if not last_user_msg:
            return False
            
        # Check if we've already answered this query
        # If the last message is from the assistant, we're done
        if self.memory.messages and self.memory.messages[-1].role == "assistant":
            # Ensure we don't loop forever
            self.state = AgentState.FINISHED
            return False
            
        # New query to process
        if not self.current_query:
            self.current_query = last_user_msg.content
            self.processing_step = "analyze_query"
            return True
            
        # Check if we need to process the query
        if self.processing_step == "analyze_query":
            self.processing_step = "research"
            return True
            
        # Check if research is complete
        if self.processing_step == "research" and not self.research_result:
            return True
            
        # All processing done
        return False
        
    async def act(self) -> str:
        """Enhanced action execution using DSPy+MCP pipeline or fallback"""
        
        if self.processing_step == "analyze_query":
            if self.use_dspy_integration:
                # Use DSPy for query analysis
                analysis = await self.dspy_mcp.analyze_query_structure(self.current_query)
                return f"📊 **Query Analysis Complete**\n\n- **Topic:** {analysis['main_topic']}\n- **Type:** {analysis['query_type']}"
            else:
                return f"📝 Analyzing query: {self.current_query[:100]}..."
                
        elif self.processing_step == "research":
            if self.use_dspy_integration:
                # Use full DSPy+MCP structured research pipeline
                print("🚀 Executing DSPy+MCP structured research pipeline...")
                self.research_result = await self.dspy_mcp.process_research_query(self.current_query)
                
                # Format the structured result
                formatted_response = self.dspy_mcp.format_research_result(self.research_result)
                
                # Add to memory and reset state
                self.update_memory("assistant", formatted_response)
                self._reset_state()
                
                return formatted_response
                
            else:
                # Fallback to basic MCP search
                print("🔍 Gathering information via basic MCP...")
                mcp_response = self.mcp_client.search(self.current_query)
                
                basic_response = f"""
## Research Results

**Query:** {self.current_query}

**Information Gathered:**
{mcp_response}

**Note:** This response uses basic MCP integration. For enhanced structured reasoning, please ensure DSPy is properly configured.
"""
                
                # Add to memory and reset state  
                self.update_memory("assistant", basic_response)
                self._reset_state()
                
                return basic_response
        
        return "Processing completed."
    
    def _reset_state(self):
        """Reset agent state for next query"""
        self.current_query = None
        self.research_result = None
        self.processing_step = None

def create_agent(name: str = "enhanced_agent", description: str = None, session_id: Optional[str] = None) -> EnhancedResearchAgent:
    """
    Factory function to create a new EnhancedResearchAgent instance.

    Args:
        name: Name of the agent
        description: Optional description of the agent
        session_id: Optional session ID for session-isolated conversation history

    Returns:
        A new EnhancedResearchAgent instance
    """
    if description is None:
        description = "Enhanced research agent with MCP integration"

    return EnhancedResearchAgent(name=name, description=description, session_id=session_id)

# Main application function
async def run_enhanced_agent(user_query: str, agent: EnhancedResearchAgent = None, session_id: Optional[str] = None) -> str:
    """
    Run the enhanced agent with a user query.

    Args:
        user_query: The user's query string
        agent: The agent instance to use. If None, a new agent will be created (legacy behavior).
        session_id: Optional session ID for session-aware processing

    Returns:
        The agent's response string
    """
    if agent is None:
        # Legacy fallback: create a new agent for backward compatibility
        agent = create_agent(session_id=session_id)
    
    # Log with privacy awareness
    logger.info_user_input("Processing agent query", user_query)
    
    try:
        result = await agent.run(user_query)
        logger.info_agent_output("Agent response generated", result)
        return result
    except Exception as e:
        logger.error(f"Agent error: {e}")
        raise

if __name__ == "__main__":
    print("🚀 Enhanced Research Agent - OpenManus + DSPy + MCP Integration")

    # Show integration status
    if dspy_mcp:
        print("✅ DSPy+MCP structured reasoning: ENABLED")
        print("📊 Available MCP servers:", dspy_mcp.mcp_client.list_servers())
        print("🎯 Default MCP server:", dspy_mcp.mcp_client.default_server)
    else:
        print("⚠️  DSPy structured reasoning: DISABLED (using basic MCP)")
        try:
            print("📊 Available MCP servers:", mcp_client.list_servers())
            print("🎯 Default MCP server:", mcp_client.default_server)
        except:
            print("❌ MCP client unavailable")

    print("-" * 50)
    print("This agent combines:")
    print("1. 🤖 OpenManus ReAct pattern for step-by-step processing")
    print("2. 🧠 DSPy structured reasoning for query analysis and response generation")
    print("3. 🔍 MCP for real-time information gathering")
    print("4. 📊 Structured pipeline: Query Analysis → Information Gathering → Synthesis → Response")
    print("-" * 50)

    # Create a session-scoped agent instance for CLI usage
    cli_agent = create_agent()

    while True:
        try:
            user_input = input("\nEnter your request (or 'quit' to exit): ")
            if user_input.lower() in ['quit', 'exit']:
                break

            result = asyncio.run(run_enhanced_agent(user_input, agent=cli_agent))
            print("\nEnhanced Agent Response:")
            print(result)

        except KeyboardInterrupt:
            print("\nGracefully shutting down...")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Try another request or 'quit' to exit") 