"""
Privacy-aware logging utility that redacts sensitive content.
"""

import re
import logging
from typing import Optional, Any
from pathlib import Path
import sys

# Add project root to path for config access
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from config.settings import get_config


class RedactedLogger:
    """
    Logger wrapper that redacts sensitive content based on privacy configuration.
    
    Usage:
        logger = RedactedLogger.get_logger(__name__)
        logger.info_user_input("User query", user_prompt)  # Redacts if configured
        logger.info_agent_output("Agent response", agent_result)  # Redacts if configured
    """
    
    def __init__(self, name: str, config: Optional[Any] = None):
        """
        Initialize redacted logger.
        
        Args:
            name: Logger name (typically __name__)
            config: Optional privacy config (loads from settings if None)
        """
        self.logger = logging.getLogger(name)
        self.config = config or get_config().privacy
        
    @classmethod
    def get_logger(cls, name: str) -> "RedactedLogger":
        """Factory method to create a RedactedLogger instance."""
        return cls(name)
    
    def _redact(self, content: str, force: bool = False) -> str:
        """
        Redact content based on configuration.
        
        Args:
            content: Content to potentially redact
            force: Force redaction regardless of config
            
        Returns:
            Original or redacted content
        """
        if not force and not self.config.redact_user_input:
            return content
            
        if not content:
            return content
            
        if self.config.show_length_hint:
            char_count = len(content)
            return f"{self.config.redaction_placeholder} ({char_count} chars)"
        else:
            return self.config.redaction_placeholder
    
    def _redact_patterns(self, content: str) -> str:
        """
        Redact known sensitive patterns (API keys, tokens, etc.).
        
        Args:
            content: Content to scan and redact
            
        Returns:
            Content with sensitive patterns redacted
        """
        patterns = [
            (r'(sk-[A-Za-z0-9_\-]{20,})', '[REDACTED_API_KEY]'),
            (r'(pk-lf-[a-z0-9\-]+)', '[REDACTED_PK]'),
            (r'(sk-lf-[a-z0-9\-]+)', '[REDACTED_SK]'),
            (r'(ghp_[A-Za-z0-9]{36})', '[REDACTED_GITHUB_TOKEN]'),
            (r'(AKIA[0-9A-Z]{16})', '[REDACTED_AWS_KEY]'),
            (r'Bearer\s+[A-Za-z0-9\-\._~\+\/]+=*', 'Bearer [REDACTED_TOKEN]'),
        ]
        
        result = content
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result)
        return result
    
    def info_user_input(self, message: str, user_input: str):
        """
        Log user input with redaction if configured.
        
        Args:
            message: Log message prefix
            user_input: The user's input to log
        """
        if self.config.redact_user_input:
            redacted = self._redact(user_input)
            self.logger.info(f"{message}: {redacted}")
        else:
            # Still redact known patterns for safety
            safe_input = self._redact_patterns(user_input)
            self.logger.info(f"{message}: {safe_input}")
    
    def debug_user_input(self, message: str, user_input: str):
        """Log user input at DEBUG level with redaction."""
        if self.config.redact_user_input:
            redacted = self._redact(user_input)
            self.logger.debug(f"{message}: {redacted}")
        else:
            safe_input = self._redact_patterns(user_input)
            self.logger.debug(f"{message}: {safe_input}")
    
    def info_agent_output(self, message: str, agent_output: str):
        """
        Log agent output with redaction if configured.
        
        Args:
            message: Log message prefix
            agent_output: The agent's output to log
        """
        if self.config.redact_agent_output:
            redacted = self._redact(agent_output)
            self.logger.info(f"{message}: {redacted}")
        else:
            # Still redact known patterns for safety
            safe_output = self._redact_patterns(agent_output)
            self.logger.info(f"{message}: {safe_output}")
    
    def info_mcp_query(self, message: str, query: str):
        """
        Log MCP query with redaction if configured.
        
        Args:
            message: Log message prefix
            query: The MCP query to log
        """
        if self.config.redact_mcp_queries:
            redacted = self._redact(query)
            self.logger.info(f"{message}: {redacted}")
        else:
            safe_query = self._redact_patterns(query)
            self.logger.info(f"{message}: {safe_query}")
    
    # Proxy standard logger methods
    def debug(self, msg: str, *args, **kwargs):
        """Standard debug logging (no redaction)."""
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        """Standard info logging (no redaction)."""
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        """Standard warning logging (no redaction)."""
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """Standard error logging (no redaction)."""
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        """Standard critical logging (no redaction)."""
        self.logger.critical(msg, *args, **kwargs)


# Convenience function for quick access
def get_redacted_logger(name: str) -> RedactedLogger:
    """
    Get a privacy-aware logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        RedactedLogger instance
        
    Example:
        from privacy.redacted_logger import get_redacted_logger
        logger = get_redacted_logger(__name__)
        logger.info_user_input("Processing query", user_query)
    """
    return RedactedLogger.get_logger(name)
