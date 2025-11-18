# Unified MCP Client Guide

## Overview

The Unified MCP Client system provides a single, consistent way to interact with multiple information sources (MCP servers) across your application. It consolidates the previous separate `mcp_client.py` and `enhanced_mcp_client.py` implementations into a unified architecture.

## Key Benefits

1. **Single Configuration Schema**: One `mcp_extended.json` config file for all MCP operations
2. **Consistent API**: Same interface whether using from CLI, UI, or API
3. **No UI/Backend Drift**: UI controls map directly to backend routing logic
4. **Full Async Support**: Non-blocking operations throughout
5. **Intelligent Routing**: Auto/manual/multi modes for server selection
6. **Environment Variable Support**: Secure API key management

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         UI Layer                            │
│  (Streamlit, FastAPI, CLI) uses routing hints API          │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              UnifiedDSPyMCPIntegration                      │
│  - Exposes routing hints via get_routing_hints()           │
│  - Provides auto/manual/multi routing modes                │
│  - Integrates DSPy structured reasoning                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              UnifiedMCPClient                               │
│  - Routes queries to appropriate servers                   │
│  - Handles multiple server types (Ollama, web, etc.)       │
│  - Full async/await support                                │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              MCPConfig + MCPConfigLoader                    │
│  - Single configuration schema                             │
│  - Environment variable substitution                       │
│  - Validation and error handling                           │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Configuration Schema

The unified configuration uses `mcp_extended.json` format:

```json
{
  "servers": {
    "server-name": {
      "type": "ollama|web_search|wikipedia|arxiv|news|github|finance|weather|playwright",
      "url": "http://...",
      "enabled": true,
      "timeout": 30,
      "model": "model-name",              // Optional: for LLM servers
      "api_key": "${ENV_VAR_NAME}",       // Optional: supports env vars
      "max_tokens": 1024,                 // Optional
      "temperature": 0.7,                 // Optional
      "capabilities": ["cap1", "cap2"],   // Optional
      "description": "Server description" // Optional
    }
  },
  "default_server": "server-name",
  "server_selection_strategy": "auto|manual|multi",
  "fallback_servers": ["server1", "server2"],
  "routing_rules": {
    "topic_name": ["server1", "server2"]
  }
}
```

### Configuration Locations

The loader searches these locations in order:
1. `enhanced_agent/config/mcp_extended.json` (recommended)
2. `enhanced_agent/config/mcp.json`
3. `config/mcp.json`
4. `mcp.json`

### Environment Variables

Use `${VAR_NAME}` syntax for sensitive data:

```json
{
  "servers": {
    "news-api": {
      "type": "news",
      "url": "https://newsapi.org/v2",
      "api_key": "${NEWS_API_KEY}"
    }
  }
}
```

Then set in your environment:
```bash
export NEWS_API_KEY="your-api-key-here"
```

### Validation

The config loader validates:
- Required fields (type, url)
- Valid server types
- Valid routing strategy
- Numeric field ranges
- Server references in routing rules

Warnings are logged for missing API keys but don't block loading.

## Routing Modes

### Auto Mode (Default)

Automatically selects the best server(s) based on query content and routing rules.

```python
# Config
"routing_rules": {
  "current_events": ["news-api", "web-search"],
  "scientific_research": ["arxiv", "web-search"]
}

# Usage
result = await client.search(
    query="What are the latest AI developments?",
    strategy=RoutingStrategy.AUTO
)
# Automatically routes to news-api or web-search
```

### Manual Mode

User explicitly specifies which server(s) to use.

```python
result = await client.search(
    query="AAPL stock price",
    servers=["finance"],
    strategy=RoutingStrategy.MANUAL
)
```

### Multi Mode

Queries multiple relevant servers and returns combined results.

```python
result = await client.search(
    query="AI research papers and trends",
    strategy=RoutingStrategy.MULTI
)
# Returns: {"arxiv": "...", "web-search": "...", "github": "..."}
```

## Usage Examples

### Basic Usage

```python
from enhanced_agent.src.unified_mcp_client import UnifiedMCPClient
from enhanced_agent.src.mcp_config import RoutingStrategy

# Initialize client (searches default config locations)
client = UnifiedMCPClient()

# Simple search with auto routing
result = await client.search("What is quantum computing?")
print(result)

# Manual server selection
result = await client.search(
    query="Python async tutorial",
    servers=["web-search", "github"]
)
print(result)

# Multi-server search
results = await client.search(
    query="Latest AI research",
    strategy=RoutingStrategy.MULTI
)
for server, content in results.items():
    print(f"\n=== From {server} ===")
    print(content)
```

### With DSPy Integration

```python
from enhanced_agent.src.unified_integration import UnifiedDSPyMCPIntegration

# Initialize integration
integration = UnifiedDSPyMCPIntegration(
    llm_model="gpt-3.5-turbo",
    dspy_cache=True
)

# Research with DSPy analysis and synthesis
result = await integration.research(
    query="What are transformer models in deep learning?",
    use_dspy=True
)

print("Query Analysis:", result["analysis"])
print("MCP Results:", result["mcp_results"])
print("Synthesized Answer:", result["synthesis"])
```

### Routing Hints for UI

```python
# Get routing configuration for UI controls
hints = integration.get_routing_hints()

# Available servers for dropdown
servers = [
    {"name": s["name"], "description": s["description"]}
    for s in hints["available_servers"]
]

# Routing strategies for radio buttons
strategies = hints["strategies"]  # ["auto", "manual", "multi"]

# Current default
default_strategy = hints["default_strategy"]

# Routing rules for display
rules = hints["routing_rules"]
```

### Context Manager

```python
async with UnifiedMCPClient() as client:
    result = await client.search("test query")
    print(result)
# Automatic cleanup
```

## UI Integration

### Streamlit Example

```python
import streamlit as st
from enhanced_agent.src.ui_integration_example import create_streamlit_ui
from enhanced_agent.src.unified_integration import UnifiedDSPyMCPIntegration

# Initialize
integration = UnifiedDSPyMCPIntegration()

# Create UI (handles all routing logic)
create_streamlit_ui(integration)
```

The UI integration helper provides:
- `get_server_choices()`: Formatted server list for dropdowns
- `get_strategy_choices()`: Routing modes for radio buttons
- `get_capability_groups()`: Servers organized by capability
- `format_routing_rules_for_display()`: Human-readable routing rules

### FastAPI Example

```python
from fastapi import FastAPI
from enhanced_agent.src.ui_integration_example import create_fastapi_endpoints
from enhanced_agent.src.unified_integration import UnifiedDSPyMCPIntegration

app = FastAPI()
integration = UnifiedDSPyMCPIntegration()

# Add endpoints
create_fastapi_endpoints(app, integration)

# Available endpoints:
# GET  /api/routing-hints
# GET  /api/servers
# GET  /api/servers/by-capability/{capability}
# POST /api/search
# POST /api/quick-search
```

## Server Types

### Supported Server Types

1. **ollama**: Local LLM server (Ollama)
2. **web_search**: DuckDuckGo web search
3. **wikipedia**: Wikipedia API
4. **arxiv**: arXiv research papers
5. **news**: News API (requires key)
6. **github**: GitHub search (optional auth)
7. **finance**: Yahoo Finance
8. **weather**: OpenWeatherMap (requires key)
9. **playwright**: Playwright MCP server

### Adding New Server Types

1. Add enum to `ServerType` in `mcp_config.py`:
```python
class ServerType(str, Enum):
    MY_SERVER = "my_server"
```

2. Implement handler in `unified_mcp_client.py`:
```python
async def _handle_my_server(self, query: str, config: ServerConfig) -> str:
    # Implementation
    pass
```

3. Register handler:
```python
def _get_handler(self, server_type: ServerType):
    handlers = {
        # ...
        ServerType.MY_SERVER: self._handle_my_server,
    }
    return handlers.get(server_type)
```

## Testing

### Run Tests

```bash
# All unified MCP tests
pytest tests/unit/test_unified_mcp.py -v

# Specific test class
pytest tests/unit/test_unified_mcp.py::TestMCPConfig -v

# With async support
pytest tests/unit/test_unified_mcp.py --asyncio-mode=auto
```

### Test Coverage

The test suite covers:
- Configuration loading and validation
- Environment variable substitution
- Server selection and routing
- All server type handlers
- Error handling and timeouts
- Context manager lifecycle
- Integration workflows

## Migration Guide

### From Old MCP Client

**Before:**
```python
from enhanced_agent.src.mcp_client import MCPClient

client = MCPClient("config/mcp.json")
result = await client.search("query", server="llama-mcp")
```

**After:**
```python
from enhanced_agent.src.unified_mcp_client import UnifiedMCPClient

client = UnifiedMCPClient()  # Auto-finds config
result = await client.search("query", servers=["llama-mcp"])
```

### From Enhanced MCP Client

**Before:**
```python
from enhanced_agent.src.enhanced_mcp_client import EnhancedMCPClient

client = EnhancedMCPClient("config/mcp_extended.json")
results = client.search("query")  # Sync
```

**After:**
```python
from enhanced_agent.src.unified_mcp_client import UnifiedMCPClient

client = UnifiedMCPClient()  # Auto-finds config
results = await client.search("query")  # Async
```

### Configuration Migration

Old configs are compatible! The unified loader handles both formats:
- Basic `mcp.json` works as-is
- Extended `mcp_extended.json` is the preferred format

To migrate, simply ensure you have `mcp_extended.json` with the full schema.

## Best Practices

1. **Use mcp_extended.json**: Provides full feature set including routing rules
2. **Set Environment Variables**: Never commit API keys to config files
3. **Enable Validation**: Let the loader validate your config on startup
4. **Use Auto Mode**: Let routing rules handle server selection
5. **Implement Fallbacks**: Configure fallback_servers for resilience
6. **Monitor Timeouts**: Adjust per-server based on response times
7. **Disable Unused Servers**: Set `enabled: false` rather than deleting
8. **Use Context Managers**: Ensure proper cleanup with `async with`

## Troubleshooting

### Config Not Found

```
FileNotFoundError: MCP config file not found
```

**Solution**: Create `enhanced_agent/config/mcp_extended.json` or specify path explicitly:
```python
client = UnifiedMCPClient("path/to/config.json")
```

### Invalid Configuration

```
ValueError: Invalid MCP configuration: Server 'x' not found
```

**Solution**: Check that all referenced servers exist in the `servers` section.

### API Key Not Set

```
Warning: Server 'news-api': API key environment variable 'NEWS_API_KEY' is not set
```

**Solution**: Set the environment variable:
```bash
export NEWS_API_KEY="your-key"
```

Or disable the server:
```json
{"enabled": false}
```

### Timeout Errors

```
Error: Timeout connecting to server
```

**Solution**: Increase timeout in config:
```json
{"timeout": 60}
```

Or check that the server is running (for local servers like Ollama).

## API Reference

See the source code documentation for complete API details:

- **`mcp_config.py`**: Configuration schema and validation
- **`unified_mcp_client.py`**: Main client implementation
- **`unified_integration.py`**: DSPy+MCP integration
- **`ui_integration_example.py`**: UI integration helpers

## Contributing

When adding features:

1. Update configuration schema in `mcp_config.py`
2. Implement handler in `unified_mcp_client.py`
3. Add tests in `tests/unit/test_unified_mcp.py`
4. Update this documentation
5. Ensure backward compatibility

## Support

For issues or questions:
- Check existing tests for usage examples
- Review `ui_integration_example.py` for integration patterns
- See `ASYNC_MCP_IMPLEMENTATION.md` for async implementation details
