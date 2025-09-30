# Centralized Configuration Management

This directory contains the new centralized configuration management system for the OMD project. This system consolidates all scattered configuration files into a unified, validated, and environment-aware solution.

## 🎯 Features

- **Centralized Configuration**: All settings in one place
- **Environment-Specific Configs**: Different settings for dev/staging/prod
- **Validation**: Pydantic-based configuration validation
- **Hot-Reloading**: Automatic configuration reload on file changes
- **Type Safety**: Full type hints and validation
- **Backward Compatibility**: Integration adapters for existing code

## 📁 Structure

```
config/
├── settings.py              # Main configuration management system
├── integrations.py          # Adapters for existing components
├── example.py              # Usage examples and demonstrations
├── requirements.txt        # Dependencies for config system
├── README.md              # This documentation
├── config.development.toml # Development environment settings
├── config.staging.toml     # Staging environment settings
├── config.production.toml  # Production environment settings
└── mcp.json               # MCP server configurations
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Using the virtual environment
./virtual/bin/pip install -r config/requirements.txt
```

### 2. Set Environment

```bash
# Set your environment (optional, defaults to development)
export ENVIRONMENT=development
```

### 3. Configure API Keys

Edit the `.env` file in the project root:

```bash
# Required for DSPy integration
OPENAI_API_KEY=your_openai_api_key_here

# Optional API keys for additional services
NEWS_API_KEY=your_news_api_key_here
WEATHER_API_KEY=your_weather_api_key_here
GITHUB_TOKEN=your_github_token_here
```

### 4. Use in Your Code

```python
from config.settings import get_config, get_llm_config, get_mcp_server_config

# Get main configuration
config = get_config()
print(f"Running in {config.environment} mode")

# Get LLM configuration
llm_config = get_llm_config()
print(f"Using {llm_config.provider} with model {llm_config.model}")

# Get MCP server configuration
server_config = get_mcp_server_config("llama-mcp")
print(f"MCP server: {server_config.url}")
```

## 🔧 Configuration Sources

The system loads configuration from multiple sources in this order:

1. **Default Values**: Sensible defaults for all settings
2. **JSON Files**: MCP server configurations
3. **TOML Files**: Environment-specific application settings
4. **Environment Variables**: From `.env` file and system environment
5. **Initialization Parameters**: Direct parameter passing

Later sources override earlier ones, allowing for flexible configuration management.

## 🌍 Environment-Specific Configuration

### Development (`config.development.toml`)
- Debug mode enabled
- Verbose logging
- Hot-reload enabled
- SQLite database
- Relaxed security settings

### Staging (`config.staging.toml`)
- Production-like settings
- Moderate logging
- PostgreSQL database
- Standard security

### Production (`config.production.toml`)
- Optimized for performance
- Minimal logging
- PostgreSQL database
- Enhanced security
- JSON structured logs

## 📊 Configuration Validation

All configuration is validated using Pydantic models:

```python
class LLMConfig(BaseSettings):
    provider: LLMProvider = Field(LLMProvider.OPENAI)
    model: str = Field("gpt-3.5-turbo")
    api_key: Optional[str] = Field(None)
    max_tokens: int = Field(2048, ge=1, le=32000)
    temperature: float = Field(0.1, ge=0.0, le=2.0)
    
    @validator('api_key', pre=True)
    def validate_api_key(cls, v, values):
        # Custom validation logic
        return v
```

Benefits:
- **Type Safety**: Catch configuration errors at startup
- **Documentation**: Self-documenting configuration schema
- **IDE Support**: Full autocomplete and type hints
- **Validation**: Ensure values are within valid ranges

## 🔄 Hot-Reloading

The configuration system automatically watches for file changes and reloads configuration:

```python
from config.settings import config_manager

def on_config_change(old_config, new_config):
    print(f"Configuration changed: {old_config.debug} -> {new_config.debug}")

# Register callback for configuration changes
config_manager.register_reload_callback(on_config_change)
```

To disable hot-reloading (e.g., in production):
```bash
export ENABLE_CONFIG_HOT_RELOAD=false
```

## 🔌 Integration with Existing Code

The system provides adapters for existing components:

### OpenManus Integration
```python
from config.integrations import OpenManusConfigAdapter

adapter = OpenManusConfigAdapter()
llm_settings = adapter.get_llm_settings()
# Returns OpenManus-compatible LLM configuration
```

### Enhanced Agent Integration
```python
from config.integrations import EnhancedAgentConfigAdapter

adapter = EnhancedAgentConfigAdapter()
mcp_config = adapter.get_mcp_config()
# Returns enhanced agent compatible MCP configuration
```

### Streamlit Integration
```python
from config.integrations import StreamlitConfigAdapter

adapter = StreamlitConfigAdapter()
st_config = adapter.get_streamlit_config()
# Returns Streamlit application configuration
```

## 🛠️ Migration from Old System

If you have existing configuration files, use the migration script:

```bash
python migrate_config.py
```

This will:
1. Backup existing configuration files
2. Extract settings from old formats
3. Create new centralized configuration files
4. Install required dependencies
5. Test the new system

## ⚙️ Advanced Usage

### Custom Configuration Sources

```python
def custom_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """Load settings from a custom source."""
    return {"custom_setting": "value"}

# Add to AppConfig.Config.customise_sources()
```

### Configuration Validation

```python
from config.settings import AppConfig

try:
    config = AppConfig()
except ValidationError as e:
    print(f"Configuration error: {e}")
```

### Environment Detection

```python
from config.settings import config_manager

if config_manager.is_production():
    # Production-specific logic
    pass
elif config_manager.is_development():
    # Development-specific logic
    pass
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Install dependencies
   ./virtual/bin/pip install -r config/requirements.txt
   ```

2. **Configuration Not Loading**
   ```bash
   # Check environment variable
   echo $ENVIRONMENT
   
   # Verify file exists
   ls config/config.development.toml
   ```

3. **API Key Validation Errors**
   ```bash
   # Check .env file
   cat .env | grep OPENAI_API_KEY
   ```

4. **Hot-Reload Not Working**
   ```bash
   # Check if watchdog is installed
   ./virtual/bin/pip show watchdog
   ```

### Debug Mode

Run the example script to debug configuration:

```bash
# Test development configuration
python config/example.py development

# Test production configuration
python config/example.py production
```

## 📚 Examples

See `config/example.py` for comprehensive usage examples including:
- Basic configuration access
- Environment-specific settings
- Hot-reload demonstration
- Integration adapter usage

## 🔒 Security Considerations

- API keys are never logged or exposed
- Production configurations disable debug features
- CORS origins are restricted in production
- Session timeouts are enforced
- Request size limits are applied

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   .env file     │    │   TOML configs   │    │   JSON configs  │
│                 │    │                  │    │                 │
│ OPENAI_API_KEY  │    │ config.dev.toml  │    │   mcp.json      │
│ NEWS_API_KEY    │────┤ config.prod.toml │────┤ mcp_ext.json    │
│ GITHUB_TOKEN    │    │ config.stg.toml  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │     ConfigManager        │
                    │                          │
                    │  • Pydantic Validation   │
                    │  • Hot-reload Support    │
                    │  • Environment Detection │
                    │  • Type Safety           │
                    └─────────────┬─────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
┌─────────▼─────────┐   ┌─────────▼─────────┐   ┌─────────▼─────────┐
│  OpenManus        │   │ Enhanced Agent    │   │   Streamlit       │
│  Adapter          │   │ Adapter           │   │   Adapter         │
│                   │   │                   │   │                   │
│ • LLM Settings    │   │ • MCP Config      │   │ • Server Config   │
│ • App Config      │   │ • DSPy Config     │   │ • Theme Settings  │
│ • Browser Config  │   │ • Agent Settings  │   │ • Security Config │
└───────────────────┘   └───────────────────┘   └───────────────────┘
```

This centralized approach eliminates configuration drift, ensures consistency across environments, and provides a single source of truth for all application settings.

