"""
Session manager for isolated conversation history with automatic cleanup.
"""

import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add project root to path for config access
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from config.settings import get_config
from privacy.redacted_logger import get_redacted_logger

logger = get_redacted_logger(__name__)


@dataclass
class SessionData:
    """Data for a single user session."""
    session_id: str
    user_id: Optional[str] = None
    messages: List[Dict[str, str]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def touch(self):
        """Update last accessed time."""
        self.last_accessed = datetime.now()
    
    def is_expired(self, timeout_seconds: int) -> bool:
        """Check if session has expired based on timeout."""
        expiry_time = self.last_accessed + timedelta(seconds=timeout_seconds)
        return datetime.now() > expiry_time
    
    def add_message(self, role: str, content: str):
        """Add a message to the session history."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.touch()
    
    def get_messages(self, max_messages: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get messages from this session.
        
        Args:
            max_messages: Maximum number of recent messages to return
            
        Returns:
            List of messages (most recent if limited)
        """
        self.touch()
        if max_messages and len(self.messages) > max_messages:
            return self.messages[-max_messages:]
        return self.messages.copy()
    
    def clear_messages(self):
        """Clear all messages in this session."""
        self.messages.clear()
        logger.info(f"Cleared messages for session {self.session_id}")


class SessionManager:
    """
    Manages isolated per-session conversation history with automatic cleanup.
    
    Features:
    - Per-session message history isolation
    - Automatic expiry and cleanup of stale sessions
    - Configurable retention policies
    - Thread-safe operations
    
    Usage:
        manager = SessionManager.get_instance()
        manager.create_session("session-123", user_id="user-456")
        manager.add_message("session-123", "user", "Hello")
        messages = manager.get_messages("session-123")
        manager.end_session("session-123")
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the session manager."""
        if not self._initialized:
            self.config = get_config().privacy
            self.sessions: Dict[str, SessionData] = {}
            self._session_lock = threading.RLock()
            self._cleanup_thread: Optional[threading.Thread] = None
            self._stop_cleanup = threading.Event()
            self._start_cleanup_thread()
            self._initialized = True
            logger.info("SessionManager initialized")
    
    @classmethod
    def get_instance(cls) -> "SessionManager":
        """Get the singleton instance."""
        return cls()
    
    def _start_cleanup_thread(self):
        """Start background thread for cleaning up expired sessions."""
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            return
        
        def cleanup_loop():
            while not self._stop_cleanup.is_set():
                try:
                    self._cleanup_expired_sessions()
                except Exception as e:
                    logger.error(f"Error in cleanup thread: {e}")
                # Check every 5 minutes
                self._stop_cleanup.wait(300)
        
        self._cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        self._cleanup_thread.start()
        logger.debug("Session cleanup thread started")
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions."""
        if not self.config.clear_history_on_timeout:
            return
        
        with self._session_lock:
            expired_sessions = [
                session_id for session_id, session in self.sessions.items()
                if session.is_expired(self.config.session_timeout_seconds)
            ]
            
            for session_id in expired_sessions:
                session = self.sessions.pop(session_id)
                logger.info(f"Cleaned up expired session: {session_id}")
                
                # Also clear Langfuse session if available
                try:
                    from langfuse_integration import langfuse_manager
                    if langfuse_manager.enabled and langfuse_manager.current_session_id == session_id:
                        langfuse_manager.clear_session()
                except Exception:
                    pass
    
    def create_session(self, session_id: str, user_id: Optional[str] = None, 
                      metadata: Optional[Dict[str, Any]] = None) -> SessionData:
        """
        Create a new session.
        
        Args:
            session_id: Unique session identifier
            user_id: Optional user identifier
            metadata: Optional metadata to store with session
            
        Returns:
            Created SessionData
        """
        with self._session_lock:
            if session_id in self.sessions:
                logger.warning(f"Session {session_id} already exists, returning existing")
                return self.sessions[session_id]
            
            session = SessionData(
                session_id=session_id,
                user_id=user_id,
                metadata=metadata or {}
            )
            self.sessions[session_id] = session
            logger.info(f"Created session: {session_id} (user: {user_id or 'anonymous'})")
            return session
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Get an existing session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionData if found, None otherwise
        """
        with self._session_lock:
            session = self.sessions.get(session_id)
            if session:
                session.touch()
            return session
    
    def add_message(self, session_id: str, role: str, content: str):
        """
        Add a message to a session.
        
        Args:
            session_id: Session identifier
            role: Message role ("user" or "assistant")
            content: Message content
        """
        with self._session_lock:
            session = self.sessions.get(session_id)
            if not session:
                logger.warning(f"Session {session_id} not found, creating new session")
                session = self.create_session(session_id)
            
            session.add_message(role, content)
            
            # Enforce max history limit
            if len(session.messages) > self.config.max_history_messages:
                excess = len(session.messages) - self.config.max_history_messages
                session.messages = session.messages[excess:]
                logger.debug(f"Trimmed {excess} old messages from session {session_id}")
    
    def get_messages(self, session_id: str, 
                    max_messages: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get messages from a session.
        
        Args:
            session_id: Session identifier
            max_messages: Optional limit on number of messages
            
        Returns:
            List of messages (empty if session not found)
        """
        with self._session_lock:
            session = self.sessions.get(session_id)
            if not session:
                logger.warning(f"Session {session_id} not found")
                return []
            return session.get_messages(max_messages)
    
    def end_session(self, session_id: str, clear_data: bool = True):
        """
        End a session and optionally clear its data.
        
        Args:
            session_id: Session identifier
            clear_data: Whether to clear session data (respects auto_clear_on_logout config)
        """
        with self._session_lock:
            session = self.sessions.get(session_id)
            if not session:
                logger.warning(f"Session {session_id} not found")
                return
            
            if clear_data and self.config.auto_clear_on_logout:
                session.clear_messages()
                del self.sessions[session_id]
                logger.info(f"Ended and cleared session: {session_id}")
            else:
                logger.info(f"Ended session (data retained): {session_id}")
                # Mark as ended but keep data
                session.metadata["ended"] = True
    
    def clear_session_messages(self, session_id: str):
        """
        Clear all messages from a session without ending it.
        
        Args:
            session_id: Session identifier
        """
        with self._session_lock:
            session = self.sessions.get(session_id)
            if session:
                session.clear_messages()
            else:
                logger.warning(f"Session {session_id} not found")
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active (non-expired) session IDs."""
        with self._session_lock:
            return [
                session_id for session_id, session in self.sessions.items()
                if not session.is_expired(self.config.session_timeout_seconds)
            ]
    
    def get_session_count(self) -> int:
        """Get total number of sessions."""
        with self._session_lock:
            return len(self.sessions)
    
    def shutdown(self):
        """Shutdown the session manager and cleanup thread."""
        logger.info("Shutting down SessionManager")
        self._stop_cleanup.set()
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=2.0)
        
        # Clear all sessions if configured
        if self.config.auto_clear_on_logout:
            with self._session_lock:
                count = len(self.sessions)
                self.sessions.clear()
                logger.info(f"Cleared {count} sessions on shutdown")


# Convenience function
def get_session_manager() -> SessionManager:
    """Get the SessionManager singleton instance."""
    return SessionManager.get_instance()
