"""
Centralized Configuration Management for OMD Project

This module provides a unified configuration system that consolidates all
configuration sources and provides validation, environment-specific configs,
and hot-reloading capabilities.
"""

import os
import json
import tomllib
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from enum import Enum
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    OLLAMA = "ollama"


class LLMConfig(BaseSettings):
    """LLM configuration settings."""
    
    provider: LLMProvider = Field(LLMProvider.OPENAI, description="LLM provider type")
    model: str = Field("gpt-3.5-turbo", description="Model name")
    api_key: Optional[str] = Field(None, description="API key for the LLM provider")
    base_url: Optional[str] = Field(None, description="Base URL for API endpoint")
    max_tokens: int = Field(2048, description="Maximum tokens per request")
    temperature: float = Field(0.1, description="Temperature for response generation")
    timeout: int = Field(60, description="Request timeout in seconds")
    
    # Azure-specific fields
    api_version: Optional[str] = Field(None, description="Azure API version")
    deployment_id: Optional[str] = Field(None, description="Azure deployment ID")
    
    @field_validator('api_key', mode='before')
    @classmethod
    def validate_api_key(cls, v, info):
        """Validate API key based on provider."""
        if info.data:
            provider = info.data.get('provider')
            if provider in [LLMProvider.OPENAI, LLMProvider.ANTHROPIC] and not v:
                # Try to get from environment
                env_key = f"{provider.upper()}_API_KEY"
                v = os.getenv(env_key)
                if not v and os.getenv('ENVIRONMENT', 'development') == 'production':
                    raise ValueError(f"API key required for {provider} in production")
        return v
    
    @field_validator('base_url', mode='before')
    @classmethod
    def set_default_base_url(cls, v, info):
        """Set default base URL based on provider."""
        if v is None and info.data:
            provider = info.data.get('provider')
            if provider == LLMProvider.OPENAI:
                return "https://api.openai.com/v1"
            elif provider == LLMProvider.ANTHROPIC:
                return "https://api.anthropic.com/v1"
            elif provider == LLMProvider.OLLAMA:
                return "http://localhost:11434/v1"
        return v


class MCPServerConfig(BaseSettings):
    """MCP server configuration."""
    
    name: str = Field(..., description="Server name")
    type: str = Field(..., description="Server type")
    url: str = Field(..., description="Server URL")
    model: Optional[str] = Field(None, description="Model name for the server")
    api_key: Optional[str] = Field(None, description="API key if required")
    timeout: int = Field(30, description="Request timeout in seconds")
    max_tokens: int = Field(1024, description="Maximum tokens per request")
    temperature: float = Field(0.7, description="Temperature setting")
    enabled: bool = Field(True, description="Whether server is enabled")
    capabilities: List[str] = Field(default_factory=list, description="Server capabilities")
    description: Optional[str] = Field(None, description="Server description")


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    
    url: Optional[str] = Field(None, description="Database URL")
    driver: str = Field("sqlite", description="Database driver")
    host: str = Field("localhost", description="Database host")
    port: int = Field(5432, description="Database port")
    name: str = Field("omd", description="Database name")
    username: Optional[str] = Field(None, description="Database username")
    password: Optional[str] = Field(None, description="Database password")
    pool_size: int = Field(10, description="Connection pool size")
    max_overflow: int = Field(20, description="Max pool overflow")
    
    @validator('url', pre=True)
    def build_url(cls, v, values):
        """Build database URL if not provided."""
        if v is None:
            driver = values.get('driver', 'sqlite')
            if driver == 'sqlite':
                return f"sqlite:///./omd.db"
            else:
                host = values.get('host', 'localhost')
                port = values.get('port', 5432)
                name = values.get('name', 'omd')
                username = values.get('username', '')
                password = values.get('password', '')
                if username and password:
                    return f"{driver}://{username}:{password}@{host}:{port}/{name}"
                else:
                    return f"{driver}://{host}:{port}/{name}"
        return v


class SecurityConfig(BaseSettings):
    """Security configuration."""
    
    secret_key: str = Field(..., description="Secret key for encryption")
    cors_origins: List[str] = Field(default_factory=lambda: ["*"], description="CORS allowed origins")
    rate_limit_per_minute: int = Field(60, description="Rate limit per minute")
    max_request_size: int = Field(10 * 1024 * 1024, description="Max request size in bytes")
    session_timeout: int = Field(3600, description="Session timeout in seconds")
    
    @validator('secret_key', pre=True)
    def validate_secret_key(cls, v):
        """Validate secret key."""
        if not v:
            v = os.getenv('SECRET_KEY')
            if not v:
                import secrets
                v = secrets.token_urlsafe(32)
        return v


class LoggingConfig(BaseSettings):
    """Logging configuration."""
    
    level: str = Field("INFO", description="Logging level")
    format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    file_path: Optional[str] = Field(None, description="Log file path")
    max_file_size: int = Field(10 * 1024 * 1024, description="Max log file size")
    backup_count: int = Field(5, description="Number of backup files")
    json_logs: bool = Field(False, description="Use JSON logging format")
    
    @validator('level')
    def validate_level(cls, v):
        """Validate logging level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return v.upper()


class LangfuseConfig(BaseSettings):
    """Langfuse observability configuration."""
    
    enabled: bool = Field(False, description="Enable Langfuse tracing")
    public_key: Optional[str] = Field(None, description="Langfuse public API key")
    secret_key: Optional[str] = Field(None, description="Langfuse secret API key")
    host: str = Field("https://cloud.langfuse.com", description="Langfuse host URL")
    
    # Tracing settings
    sample_rate: float = Field(1.0, description="Sampling rate for traces (0.0 to 1.0)")
    flush_at: int = Field(15, description="Number of events to batch before sending")
    flush_interval: float = Field(0.5, description="Interval in seconds to flush events")
    
    # Feature flags
    trace_llm_calls: bool = Field(True, description="Trace LLM API calls")
    trace_agent_steps: bool = Field(True, description="Trace agent reasoning steps")
    trace_mcp_calls: bool = Field(True, description="Trace MCP server calls")
    
    # Cost tracking
    track_costs: bool = Field(True, description="Track and calculate costs")
    
    @validator('public_key', 'secret_key', pre=True)
    def validate_keys(cls, v, field):
        """Validate Langfuse keys from environment."""
        if v is None:
            env_var = f"LANGFUSE_{field.name.upper()}"
            v = os.getenv(env_var)
        return v
    
    @validator('sample_rate')
    def validate_sample_rate(cls, v):
        """Validate sample rate is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Sample rate must be between 0.0 and 1.0")
        return v


class AppConfig(BaseSettings):
    """Main application configuration."""
    
    # Environment settings
    environment: Environment = Field(Environment.DEVELOPMENT, description="Application environment")
    debug: bool = Field(True, description="Debug mode")
    version: str = Field("1.0.0", description="Application version")
    
    # Server settings
    host: str = Field("localhost", description="Server host")
    port: int = Field(8503, description="Server port")
    workers: int = Field(1, description="Number of worker processes")
    
    # Application settings
    max_steps: int = Field(10, description="Maximum agent steps")
    request_timeout: int = Field(300, description="Request timeout in seconds")
    enable_sandbox: bool = Field(True, description="Enable sandbox environment")
    
    # Feature flags
    enable_dspy: bool = Field(True, description="Enable DSPy integration")
    enable_mcp: bool = Field(True, description="Enable MCP integration")
    enable_metrics: bool = Field(False, description="Enable metrics collection")
    enable_tracing: bool = Field(False, description="Enable request tracing")
    
    # Component configurations
    llm: LLMConfig = Field(default_factory=LLMConfig, description="LLM configuration")
    llm_vision: Optional[LLMConfig] = Field(None, description="Vision LLM configuration")
    database: DatabaseConfig = Field(default_factory=DatabaseConfig, description="Database configuration")
    security: SecurityConfig = Field(default_factory=SecurityConfig, description="Security configuration")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="Logging configuration")
    langfuse: LangfuseConfig = Field(default_factory=LangfuseConfig, description="Langfuse observability configuration")
    
    # MCP servers
    mcp_servers: Dict[str, MCPServerConfig] = Field(default_factory=dict, description="MCP server configurations")
    default_mcp_server: str = Field("llama-mcp", description="Default MCP server")
    
    @validator('environment', pre=True)
    def validate_environment(cls, v):
        """Validate and normalize environment."""
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    @root_validator
    def validate_production_settings(cls, values):
        """Validate production-specific settings."""
        env = values.get('environment')
        if env == Environment.PRODUCTION:
            # Ensure debug is False in production
            values['debug'] = False
            
            # Ensure critical settings are configured
            llm = values.get('llm', {})
            if isinstance(llm, dict) and not llm.get('api_key'):
                raise ValueError("LLM API key is required in production")
                
        return values
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            """Customize settings sources to include config files."""
            return (
                init_settings,
                env_settings,
                file_secret_settings,
                toml_settings_source,
                json_settings_source,
            )


def toml_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """Load settings from TOML files."""
    config_data = {}
    
    # Look for environment-specific config first
    env = os.getenv('ENVIRONMENT', 'development')
    config_files = [
        f"config/config.{env}.toml",
        "config/config.toml",
        "OpenManus/config/config.toml",
    ]
    
    for config_file in config_files:
        if Path(config_file).exists():
            with open(config_file, 'rb') as f:
                config_data.update(tomllib.load(f))
            break
    
    return config_data


def json_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """Load settings from JSON files."""
    config_data = {}
    
    # Load MCP configurations
    mcp_files = [
        "config/mcp.json",
        "enhanced_agent/config/mcp_extended.json",
        "enhanced_agent/config/mcp.json",
    ]
    
    mcp_servers = {}
    for mcp_file in mcp_files:
        if Path(mcp_file).exists():
            with open(mcp_file, 'r') as f:
                mcp_data = json.load(f)
                
            # Extract servers
            if 'servers' in mcp_data:
                for name, server_config in mcp_data['servers'].items():
                    server_config['name'] = name
                    mcp_servers[name] = server_config
                    
            # Extract default server
            if 'default_server' in mcp_data:
                config_data['default_mcp_server'] = mcp_data['default_server']
    
    if mcp_servers:
        config_data['mcp_servers'] = mcp_servers
    
    return config_data


class ConfigFileHandler(FileSystemEventHandler):
    """Handle configuration file changes for hot-reloading."""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self._last_reload = 0
        self._reload_debounce = 1.0  # seconds
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
            
        # Check if it's a config file
        config_extensions = ['.toml', '.json', '.env']
        if any(event.src_path.endswith(ext) for ext in config_extensions):
            current_time = time.time()
            if current_time - self._last_reload > self._reload_debounce:
                self._last_reload = current_time
                self.config_manager.reload()


class ConfigManager:
    """Centralized configuration manager with hot-reloading support."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._config = None
            self._observer = None
            self._callbacks = []
            self._load_config()
            self._setup_hot_reload()
            self._initialized = True
    
    def _load_config(self):
        """Load configuration from all sources."""
        try:
            self._config = AppConfig()
        except Exception as e:
            print(f"Error loading configuration: {e}")
            # Load minimal default config
            self._config = AppConfig(
                environment=Environment.DEVELOPMENT,
                debug=True
            )
    
    def _setup_hot_reload(self):
        """Set up file watching for hot-reloading."""
        if os.getenv('ENABLE_CONFIG_HOT_RELOAD', 'true').lower() == 'true':
            try:
                self._observer = Observer()
                handler = ConfigFileHandler(self)
                
                # Watch config directories
                watch_paths = ['config', 'enhanced_agent/config', 'OpenManus/config', '.']
                for path in watch_paths:
                    if Path(path).exists():
                        self._observer.schedule(handler, path, recursive=False)
                
                self._observer.start()
            except Exception as e:
                print(f"Could not set up config hot-reload: {e}")
    
    def reload(self):
        """Reload configuration from files."""
        print("🔄 Reloading configuration...")
        old_config = self._config
        self._load_config()
        
        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(old_config, self._config)
            except Exception as e:
                print(f"Error in config reload callback: {e}")
        
        print("✅ Configuration reloaded")
    
    def register_reload_callback(self, callback):
        """Register a callback for configuration reloads."""
        self._callbacks.append(callback)
    
    def get_config(self) -> AppConfig:
        """Get the current configuration."""
        return self._config
    
    def get_llm_config(self, config_name: str = "default") -> LLMConfig:
        """Get LLM configuration by name."""
        if config_name == "vision" and self._config.llm_vision:
            return self._config.llm_vision
        return self._config.llm
    
    def get_mcp_server_config(self, server_name: Optional[str] = None) -> Optional[MCPServerConfig]:
        """Get MCP server configuration."""
        if server_name is None:
            server_name = self._config.default_mcp_server
        
        server_dict = self._config.mcp_servers.get(server_name)
        if server_dict:
            if isinstance(server_dict, dict):
                return MCPServerConfig(**server_dict)
            return server_dict
        return None
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self._config.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self._config.environment == Environment.DEVELOPMENT
    
    def stop(self):
        """Stop the configuration manager and cleanup."""
        if self._observer:
            self._observer.stop()
            self._observer.join()


# Global configuration manager instance
config_manager = ConfigManager()


def get_config() -> AppConfig:
    """Get the current application configuration."""
    return config_manager.get_config()


def get_llm_config(config_name: str = "default") -> LLMConfig:
    """Get LLM configuration."""
    return config_manager.get_llm_config(config_name)


def get_mcp_server_config(server_name: Optional[str] = None) -> Optional[MCPServerConfig]:
    """Get MCP server configuration."""
    return config_manager.get_mcp_server_config(server_name)


def reload_config():
    """Reload configuration from files."""
    config_manager.reload()


# Cleanup on exit
import atexit
atexit.register(config_manager.stop)

