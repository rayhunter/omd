#!/usr/bin/env python3
"""
Example usage of the centralized configuration management system.

This demonstrates how to use the new configuration system in your applications.
"""

import os
import sys
from pathlib import Path

# Project root
project_root = Path(__file__).parent.parent

from config.settings import get_config, get_llm_config, get_mcp_server_config, config_manager


def main():
    """Demonstrate the configuration system."""
    
    print("🔧 OMD Centralized Configuration System Demo")
    print("=" * 50)
    
    # Get the main configuration
    config = get_config()
    
    print(f"Environment: {config.environment}")
    print(f"Debug mode: {config.debug}")
    print(f"Version: {config.version}")
    print(f"Host: {config.host}:{config.port}")
    print()
    
    # Get LLM configuration
    llm_config = get_llm_config()
    print("LLM Configuration:")
    print(f"  Provider: {llm_config.provider}")
    print(f"  Model: {llm_config.model}")
    print(f"  Max tokens: {llm_config.max_tokens}")
    print(f"  Temperature: {llm_config.temperature}")
    print(f"  Base URL: {llm_config.base_url}")
    print(f"  API Key: {'***' if llm_config.api_key else 'Not set'}")
    print()
    
    # Get vision LLM configuration
    vision_config = get_llm_config("vision")
    if vision_config:
        print("Vision LLM Configuration:")
        print(f"  Provider: {vision_config.provider}")
        print(f"  Model: {vision_config.model}")
        print()
    
    # Get MCP server configurations
    print("MCP Server Configurations:")
    print(f"  Default server: {config.default_mcp_server}")
    
    for server_name in config.mcp_servers.keys():
        server_config = get_mcp_server_config(server_name)
        if server_config:
            print(f"  {server_name}:")
            print(f"    Type: {server_config.type}")
            print(f"    URL: {server_config.url}")
            print(f"    Enabled: {server_config.enabled}")
            print(f"    Timeout: {server_config.timeout}s")
            if server_config.capabilities:
                print(f"    Capabilities: {', '.join(server_config.capabilities)}")
    print()
    
    # Database configuration
    print("Database Configuration:")
    print(f"  Driver: {config.database.driver}")
    print(f"  URL: {config.database.url}")
    print(f"  Pool size: {config.database.pool_size}")
    print()
    
    # Security configuration
    print("Security Configuration:")
    print(f"  CORS origins: {config.security.cors_origins}")
    print(f"  Rate limit: {config.security.rate_limit_per_minute}/min")
    print(f"  Max request size: {config.security.max_request_size} bytes")
    print()
    
    # Logging configuration
    print("Logging Configuration:")
    print(f"  Level: {config.logging.level}")
    print(f"  File path: {config.logging.file_path}")
    print(f"  JSON logs: {config.logging.json_logs}")
    print()
    
    # Feature flags
    print("Feature Flags:")
    print(f"  DSPy enabled: {config.enable_dspy}")
    print(f"  MCP enabled: {config.enable_mcp}")
    print(f"  Metrics enabled: {config.enable_metrics}")
    print(f"  Tracing enabled: {config.enable_tracing}")
    print()
    
    # Environment-specific information
    if config_manager.is_development():
        print("🚧 Running in DEVELOPMENT mode")
        print("  - Debug logging enabled")
        print("  - Hot-reload enabled")
        print("  - Extended timeouts")
    elif config_manager.is_production():
        print("🏭 Running in PRODUCTION mode")
        print("  - Optimized for performance")
        print("  - Enhanced security")
        print("  - Structured logging")
    else:
        print(f"🔧 Running in {config.environment.upper()} mode")
    
    print()
    print("💡 Configuration loaded from:")
    print("  - Environment variables (.env file)")
    print("  - TOML configuration files")
    print("  - JSON MCP configurations")
    print("  - Default values with validation")


def demonstrate_hot_reload():
    """Demonstrate hot-reload functionality."""
    
    print("\n🔄 Hot-reload Demonstration")
    print("=" * 30)
    
    def on_config_change(old_config, new_config):
        """Callback for configuration changes."""
        print(f"Configuration changed!")
        print(f"  Environment: {old_config.environment} → {new_config.environment}")
        print(f"  Debug: {old_config.debug} → {new_config.debug}")
    
    # Register callback
    config_manager.register_reload_callback(on_config_change)
    
    print("Configuration hot-reload is active.")
    print("Try editing config files to see changes reflected automatically.")
    print("Press Ctrl+C to exit...")
    
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down configuration manager...")
        config_manager.stop()


if __name__ == "__main__":
    # Set environment for demonstration
    if len(sys.argv) > 1:
        os.environ['ENVIRONMENT'] = sys.argv[1]
    else:
        os.environ['ENVIRONMENT'] = 'development'
    
    main()
    
    # Uncomment to test hot-reload
    # demonstrate_hot_reload()

