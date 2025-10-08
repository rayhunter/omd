"""
Configuration helper for both local and cloud environments.
Handles .env files (local) and Streamlit secrets (cloud).
"""

import os
from typing import Optional, Any

def get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get configuration value from environment variables or Streamlit secrets.
    
    Priority:
    1. Environment variable (os.getenv)
    2. Streamlit secrets (if available)
    3. Default value
    
    Args:
        key: Configuration key to look up
        default: Default value if not found
        
    Returns:
        Configuration value or default
    """
    # First try environment variable
    value = os.getenv(key)
    if value:
        return value
    
    # Then try Streamlit secrets (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and st.secrets:
            # Try different secret formats
            if key in st.secrets:
                return st.secrets[key]
            
            # Try nested secrets (e.g., st.secrets["api_keys"]["openai"])
            if "." in key:
                keys = key.split(".")
                current = st.secrets
                for k in keys:
                    if isinstance(current, dict) and k in current:
                        current = current[k]
                    else:
                        current = None
                        break
                if current:
                    return current
    except Exception:
        pass
    
    # Return default if nothing found
    return default

def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key from environment or secrets."""
    return get_config_value("OPENAI_API_KEY")

def get_langfuse_config() -> dict:
    """Get Langfuse configuration from environment or secrets."""
    return {
        "public_key": get_config_value("LANGFUSE_PUBLIC_KEY"),
        "secret_key": get_config_value("LANGFUSE_SECRET_KEY"),
        "host": get_config_value("LANGFUSE_HOST", "https://us.cloud.langfuse.com")
    }

def is_cloud_environment() -> bool:
    """Check if running in Streamlit Cloud."""
    return os.getenv("STREAMLIT_CLOUD") is not None

def get_model_config() -> str:
    """Get the appropriate model for the current environment."""
    if is_cloud_environment():
        # Use Hugging Face model for cloud
        return get_config_value("LLM_MODEL", "microsoft/Phi-3-mini-4k-instruct")
    else:
        # Use local Ollama model
        return get_config_value("LLM_MODEL", "gemma2:2b")
