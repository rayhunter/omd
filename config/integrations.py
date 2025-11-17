"""
Integration adapters for the centralized configuration system.

This module provides adapters to integrate the new configuration system
with existing OpenManus and enhanced_agent components.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

# Project root
project_root = Path(__file__).parent.parent

from config.settings import get_config, get_llm_config, get_mcp_server_config, config_manager


class OpenManusConfigAdapter:
    """Adapter to provide OpenManus-compatible configuration."""
    
    @staticmethod
    def get_llm_settings() -> Dict[str, Any]:
        """Get LLM settings in OpenManus format."""
        config = get_config()
        llm_config = get_llm_config()
        
        # Convert to OpenManus LLMSettings format
        settings = {
            "default": {
                "model": llm_config.model,
                "api_key": llm_config.api_key,
                "base_url": llm_config.base_url,
                "max_tokens": llm_config.max_tokens,
                "temperature": llm_config.temperature,
                "api_type": llm_config.provider.value,
            }
        }
        
        # Add vision config if available
        if config.llm_vision:
            vision_config = get_llm_config("vision")
            settings["vision"] = {
                "model": vision_config.model,
                "api_key": vision_config.api_key,
                "base_url": vision_config.base_url,
                "max_tokens": vision_config.max_tokens,
                "temperature": vision_config.temperature,
                "api_type": vision_config.provider.value,
            }
            
        # Add Azure-specific fields
        if llm_config.provider.value == "azure":
            settings["default"]["api_version"] = llm_config.api_version
            if config.llm_vision and config.llm_vision.provider.value == "azure":
                settings["vision"]["api_version"] = config.llm_vision.api_version
        
        return settings
    
    @staticmethod
    def get_app_config() -> Dict[str, Any]:
        """Get application config in OpenManus format."""
        config = get_config()
        
        return {
            "debug": config.debug,
            "environment": config.environment.value,
            "max_steps": config.max_steps,
            "enable_sandbox": config.enable_sandbox,
            "request_timeout": config.request_timeout,
        }
    
    @staticmethod
    def get_browser_config() -> Dict[str, Any]:
        """Get browser configuration."""
        config = get_config()
        
        # Default browser settings
        browser_config = {
            "headless": not config.debug,  # Run headless in non-debug mode
            "disable_security": config.debug,  # Disable security in debug mode
            "extra_chromium_args": [],
            "chrome_instance_path": "",
            "wss_url": "",
            "cdp_url": "",
        }
        
        return browser_config


class EnhancedAgentConfigAdapter:
    """Adapter to provide enhanced agent compatible configuration."""
    
    @staticmethod
    def get_mcp_config() -> Dict[str, Any]:
        """Get MCP configuration in enhanced agent format."""
        config = get_config()
        
        mcp_config = {
            "servers": {},
            "default_server": config.default_mcp_server,
            "routing_rules": {}
        }
        
        # Convert server configurations
        for server_name, server_dict in config.mcp_servers.items():
            server_config = get_mcp_server_config(server_name)
            if server_config and server_config.enabled:
                mcp_config["servers"][server_name] = {
                    "type": server_config.type,
                    "url": server_config.url,
                    "model": server_config.model,
                    "timeout": server_config.timeout,
                    "max_tokens": server_config.max_tokens,
                    "temperature": server_config.temperature,
                    "api_key": server_config.api_key,
                    "context_length": getattr(server_config, 'context_length', 4096),
                    "description": server_config.description,
                    "capabilities": server_config.capabilities,
                }
        
        return mcp_config
    
    @staticmethod
    def get_dspy_config() -> Dict[str, Any]:
        """Get DSPy configuration."""
        config = get_config()
        llm_config = get_llm_config()
        
        return {
            "enabled": config.enable_dspy,
            "llm_model": llm_config.model,
            "api_key": llm_config.api_key,
            "base_url": llm_config.base_url,
            "max_tokens": llm_config.max_tokens,
            "temperature": llm_config.temperature,
            "cache": config.debug,  # Enable cache in debug mode
        }
    
    @staticmethod
    def get_agent_config() -> Dict[str, Any]:
        """Get agent configuration."""
        config = get_config()
        
        return {
            "max_steps": config.max_steps,
            "timeout": config.request_timeout,
            "enable_mcp": config.enable_mcp,
            "enable_dspy": config.enable_dspy,
            "debug": config.debug,
        }


class StreamlitConfigAdapter:
    """Adapter for Streamlit application configuration."""
    
    @staticmethod
    def get_streamlit_config() -> Dict[str, Any]:
        """Get Streamlit configuration."""
        config = get_config()
        
        return {
            "server": {
                "port": config.port,
                "address": config.host,
                "headless": not config.debug,
                "enableCORS": True,
                "enableXsrfProtection": config.environment.value == "production",
            },
            "browser": {
                "gatherUsageStats": False,
            },
            "logger": {
                "level": config.logging.level,
            },
            "theme": {
                "primaryColor": "#f59e0b",        # Warm amber
                "backgroundColor": "#fefce8",      # Cream
                "secondaryBackgroundColor": "#fef9c3",  # Light yellow
                "textColor": "#292524",           # Warm stone
                "font": "Manrope",                 # Friendly, rounded modern font
            }
        }
    
    @staticmethod
    def get_app_settings() -> Dict[str, Any]:
        """Get application settings for Streamlit."""
        config = get_config()
        
        return {
            "title": "Enhanced Research Agent",
            "page_icon": "🧠",
            "layout": "wide",
            "initial_sidebar_state": "expanded",
            "debug": config.debug,
            "enable_metrics": config.enable_metrics,
            "enable_tracing": config.enable_tracing,
            "max_request_size": config.security.max_request_size,
            "session_timeout": config.security.session_timeout,
        }


def patch_openmanus_config():
    """Patch OpenManus to use the centralized configuration."""
    try:
        # Import OpenManus config module
        from OpenManus.app.config import Config as OpenManusConfig
        
        # Store original methods
        original_get_config = getattr(OpenManusConfig, '_get_config_path', None)
        
        # Create adapter instance
        adapter = OpenManusConfigAdapter()
        
        # Patch the config loading
        def patched_load_config(self):
            """Load config using centralized system."""
            config_data = {
                "llm": adapter.get_llm_settings(),
                "app": adapter.get_app_config(),
                "browser": adapter.get_browser_config(),
            }
            return config_data
        
        # Apply patch
        if hasattr(OpenManusConfig, '_load_config'):
            OpenManusConfig._load_config = patched_load_config
            print("✅ OpenManus configuration patched successfully")
        
    except ImportError:
        print("⚠️  OpenManus not available for configuration patching")
    except Exception as e:
        print(f"❌ Error patching OpenManus configuration: {e}")


def patch_enhanced_agent_config():
    """Patch enhanced agent to use the centralized configuration."""
    try:
        # Import enhanced agent modules
        from dspy_mcp_integration import DSPyMCPIntegration
        from mcp_client import MCPClient
        
        adapter = EnhancedAgentConfigAdapter()
        
        # Patch MCP client initialization
        original_mcp_init = MCPClient.__init__
        
        def patched_mcp_init(self, config_file: str = None):
            """Initialize MCP client with centralized config."""
            # Use centralized configuration instead of file
            mcp_config = adapter.get_mcp_config()
            self.config = mcp_config
            self.default_server = mcp_config.get("default_server", "llama-mcp")
        
        MCPClient.__init__ = patched_mcp_init
        
        # Patch DSPy integration
        original_dspy_init = DSPyMCPIntegration.__init__
        
        def patched_dspy_init(self, mcp_config_path: str = None, llm_model: str = None, dspy_cache: bool = None):
            """Initialize DSPy integration with centralized config."""
            dspy_config = adapter.get_dspy_config()
            agent_config = adapter.get_agent_config()
            
            # Use centralized config values
            llm_model = llm_model or dspy_config["llm_model"]
            dspy_cache = dspy_cache if dspy_cache is not None else dspy_config["cache"]
            
            # Call original with centralized values
            original_dspy_init(self, None, llm_model, dspy_cache)
        
        DSPyMCPIntegration.__init__ = patched_dspy_init
        
        print("✅ Enhanced agent configuration patched successfully")
        
    except ImportError:
        print("⚠️  Enhanced agent modules not available for configuration patching")
    except Exception as e:
        print(f"❌ Error patching enhanced agent configuration: {e}")


def apply_all_patches():
    """Apply all configuration patches."""
    print("🔧 Applying centralized configuration patches...")
    patch_openmanus_config()
    patch_enhanced_agent_config()
    print("✅ All configuration patches applied")


def setup_environment_config():
    """Set up environment-specific configuration."""
    config = get_config()
    
    # Set environment variables for compatibility
    os.environ['ENVIRONMENT'] = config.environment.value
    os.environ['DEBUG'] = str(config.debug).lower()
    
    # Set LLM environment variables
    llm_config = get_llm_config()
    if llm_config.api_key:
        if llm_config.provider.value == "openai":
            os.environ['OPENAI_API_KEY'] = llm_config.api_key
        elif llm_config.provider.value == "anthropic":
            os.environ['ANTHROPIC_API_KEY'] = llm_config.api_key
    
    # Set MCP environment variables
    for server_name, server_dict in config.mcp_servers.items():
        server_config = get_mcp_server_config(server_name)
        if server_config and server_config.api_key:
            env_key = f"{server_name.upper().replace('-', '_')}_API_KEY"
            os.environ[env_key] = server_config.api_key
    
    print(f"✅ Environment configured for {config.environment.value}")


# Auto-setup when module is imported
if __name__ != "__main__":
    setup_environment_config()


if __name__ == "__main__":
    """Test the integration adapters."""
    print("🧪 Testing Configuration Integration Adapters")
    print("=" * 50)
    
    # Test OpenManus adapter
    print("Testing OpenManus adapter...")
    adapter = OpenManusConfigAdapter()
    llm_settings = adapter.get_llm_settings()
    print(f"LLM settings: {llm_settings}")
    
    # Test Enhanced Agent adapter
    print("\nTesting Enhanced Agent adapter...")
    ea_adapter = EnhancedAgentConfigAdapter()
    mcp_config = ea_adapter.get_mcp_config()
    print(f"MCP config: {list(mcp_config['servers'].keys())}")
    
    # Test Streamlit adapter
    print("\nTesting Streamlit adapter...")
    st_adapter = StreamlitConfigAdapter()
    st_config = st_adapter.get_streamlit_config()
    print(f"Streamlit server config: {st_config['server']}")
    
    print("\n✅ All adapters tested successfully")

