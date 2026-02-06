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

def get_llm_provider_config() -> dict:
    """
    Get LLM provider configuration based on environment and available API keys.
    
    Priority for cloud environments:
    1. OpenAI (if OPENAI_API_KEY is set)
    2. Anthropic (if ANTHROPIC_API_KEY is set)
    3. Fallback to Ollama (local only)
    
    Returns:
        dict with: provider, api_key, base_url, model
    """
    is_cloud = is_cloud_environment()
    
    # Cloud environment - check for API keys
    if is_cloud:
        openai_key = get_config_value("OPENAI_API_KEY")
        if openai_key:
            return {
                "provider": "openai",
                "api_key": openai_key,
                "base_url": get_config_value("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                "model": get_config_value("OPENAI_MODEL", "gpt-4o-mini")
            }
        
        anthropic_key = get_config_value("ANTHROPIC_API_KEY")
        if anthropic_key:
            return {
                "provider": "anthropic",
                "api_key": anthropic_key,
                "base_url": get_config_value("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1"),
                "model": get_config_value("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
            }
        
        # No API keys found in cloud - error state
        print("⚠️  WARNING: Running in cloud environment but no LLM API keys found!")
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your environment variables.")
        # Return a placeholder that will fail gracefully
        return {
            "provider": "none",
            "api_key": None,
            "base_url": None,
            "model": None
        }
    
    # Local environment - use Ollama
    return {
        "provider": "ollama",
        "api_key": "ollama",
        "base_url": get_config_value("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        "model": get_config_value("OLLAMA_MODEL", "gemma2:2b")
    }

def is_cloud_environment() -> bool:
    """Check if running in Streamlit Cloud or Railway."""
    # #region agent log
    import json
    env_vars = {'STREAMLIT_CLOUD': os.getenv('STREAMLIT_CLOUD'), 'RAILWAY_ENVIRONMENT': os.getenv('RAILWAY_ENVIRONMENT'), 'RAILWAY_PROJECT_ID': os.getenv('RAILWAY_PROJECT_ID'), 'PORT': os.getenv('PORT')}
    result = (
        os.getenv("STREAMLIT_CLOUD") is not None or
        os.getenv("RAILWAY_ENVIRONMENT") is not None or
        os.getenv("RAILWAY_PROJECT_ID") is not None
    )
    log_path = '/Users/raymondhunter/LocalProjects/10workspaceOct25/omd/.cursor/debug.log'
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({'sessionId': 'debug-session', 'runId': 'run2', 'hypothesisId': 'A', 'location': 'config_helper.py:68', 'message': 'is_cloud_environment check (FIXED)', 'data': {'env_vars': env_vars, 'result': result}, 'timestamp': __import__('time').time() * 1000}) + '\n')
    except: pass
    # #endregion
    return (
        os.getenv("STREAMLIT_CLOUD") is not None or
        os.getenv("RAILWAY_ENVIRONMENT") is not None or
        os.getenv("RAILWAY_PROJECT_ID") is not None
    )

def get_model_config() -> str:
    """Get the appropriate model for the current environment."""
    # #region agent log
    import json
    # #endregion
    
    # Use the new provider config function
    provider_config = get_llm_provider_config()
    result = provider_config["model"]
    
    # #region agent log
    log_path = '/Users/raymondhunter/LocalProjects/10workspaceOct25/omd/.cursor/debug.log'
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps({'sessionId': 'debug-session', 'runId': 'run2', 'hypothesisId': 'B', 'location': 'config_helper.py:72', 'message': 'get_model_config decision (FIXED)', 'data': {'provider': provider_config['provider'], 'model': result, 'is_cloud': is_cloud_environment()}, 'timestamp': __import__('time').time() * 1000}) + '\n')
    except: pass
    # #endregion
    
    return result
