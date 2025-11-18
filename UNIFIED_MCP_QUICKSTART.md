# Unified MCP Client - Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
# Already installed if using the project
# Otherwise:
pip install httpx asyncio
```

### 2. Configuration (Optional)
Use the existing `enhanced_agent/config/mcp_extended.json` or create your own:

```json
{
  "servers": {
    "llama-mcp": {
      "type": "ollama",
      "url": "http://localhost:11434",
      "model": "gemma2:2b",
      "enabled": true,
      "timeout": 60,
      "capabilities": ["general_knowledge"]
    }
  },
  "default_server": "llama-mcp",
  "server_selection_strategy": "auto"
}
```

### 3. Basic Usage

```python
import asyncio
from enhanced_agent.src.unified_mcp_client import UnifiedMCPClient

async def main():
    # Initialize client (auto-finds config)
    client = UnifiedMCPClient()

    # Simple search
    result = await client.search("What is Python?")
    print(result)

asyncio.run(main())
```

That's it! 🎉

## Common Use Cases

### Use Case 1: Auto-Routing Based on Query

```python
from enhanced_agent.src.unified_mcp_client import UnifiedMCPClient
from enhanced_agent.src.mcp_config import RoutingStrategy

client = UnifiedMCPClient()

# Auto-selects best server based on routing rules
result = await client.search(
    "What are the latest AI developments?",
    strategy=RoutingStrategy.AUTO
)
```

### Use Case 2: Manual Server Selection

```python
# Explicitly choose which server(s) to use
result = await client.search(
    "AAPL stock price",
    servers=["finance"]
)
```

### Use Case 3: Multi-Server Search

```python
# Query multiple servers and get all results
results = await client.search(
    "AI research trends",
    strategy=RoutingStrategy.MULTI
)

# Results format: {"server1": "result1", "server2": "result2"}
for server, content in results.items():
    print(f"\n=== {server} ===")
    print(content)
```

### Use Case 4: With DSPy Integration

```python
from enhanced_agent.src.unified_integration import UnifiedDSPyMCPIntegration

# Initialize with DSPy structured reasoning
integration = UnifiedDSPyMCPIntegration(
    llm_model="gpt-3.5-turbo",
    dspy_cache=True
)

# Research with analysis and synthesis
result = await integration.research(
    query="What are transformer models?",
    use_dspy=True
)

print("Analysis:", result["analysis"])
print("Answer:", result["synthesis"]["answer"])
```

### Use Case 5: Building a UI

```python
import streamlit as st
from enhanced_agent.src.unified_integration import UnifiedDSPyMCPIntegration
from enhanced_agent.src.ui_integration_example import UIIntegrationHelper

# Initialize
integration = UnifiedDSPyMCPIntegration()
helper = UIIntegrationHelper(integration)

# Get routing hints for UI controls
hints = helper.get_routing_hints()

# Create dropdown from actual available servers
servers = [s["name"] for s in hints["available_servers"]]
selected = st.selectbox("Choose server:", servers)

# Execute search
if st.button("Search"):
    result = await integration.quick_search(
        query=st.text_input("Query:"),
        servers=[selected]
    )
    st.write(result)
```

## Configuration Options

### Minimal Config
```json
{
  "servers": {
    "my-server": {
      "type": "ollama",
      "url": "http://localhost:11434"
    }
  },
  "default_server": "my-server"
}
```

### Full Config
```json
{
  "servers": {
    "my-server": {
      "type": "ollama",
      "url": "http://localhost:11434",
      "model": "llama2",
      "enabled": true,
      "timeout": 30,
      "max_tokens": 1024,
      "temperature": 0.7,
      "api_key": "${API_KEY}",
      "capabilities": ["general_knowledge"],
      "description": "My local LLM"
    }
  },
  "default_server": "my-server",
  "server_selection_strategy": "auto",
  "fallback_servers": ["my-server"],
  "routing_rules": {
    "topic_name": ["server1", "server2"]
  }
}
```

## Supported Server Types

| Type | Description | Requires API Key |
|------|-------------|------------------|
| `ollama` | Local Ollama LLM | No |
| `web_search` | DuckDuckGo search | No |
| `wikipedia` | Wikipedia API | No |
| `arxiv` | Research papers | No |
| `news` | News API | Yes (NEWS_API_KEY) |
| `github` | GitHub search | Optional (GITHUB_TOKEN) |
| `finance` | Yahoo Finance | No |
| `weather` | OpenWeatherMap | Yes (WEATHER_API_KEY) |
| `playwright` | Playwright MCP | No |

## Environment Variables

For servers requiring API keys:

```bash
# .env file or export
export NEWS_API_KEY="your-key-here"
export GITHUB_TOKEN="your-token-here"
export WEATHER_API_KEY="your-key-here"
```

In config, use:
```json
{
  "api_key": "${NEWS_API_KEY}"
}
```

## Routing Strategies

### Auto (Default)
```python
# Automatically selects based on routing rules
result = await client.search("query")
```

**When to use:** Let the system choose based on query content

### Manual
```python
# You choose the server(s)
result = await client.search("query", servers=["server1", "server2"])
```

**When to use:** You know exactly which server to query

### Multi
```python
# Query multiple servers concurrently
result = await client.search("query", strategy=RoutingStrategy.MULTI)
```

**When to use:** Need results from multiple sources

## Routing Rules

Define in config to enable auto-routing:

```json
{
  "routing_rules": {
    "current_events": ["news-api", "web-search"],
    "scientific_research": ["arxiv", "wikipedia"],
    "code_related": ["github"],
    "financial": ["finance"]
  }
}
```

Query containing keywords like "current" or "events" → uses news-api and web-search

## Error Handling

```python
try:
    result = await client.search("query")

    if result.startswith("Error:"):
        print(f"Search failed: {result}")
    else:
        print(f"Success: {result}")

except Exception as e:
    print(f"Exception: {e}")
```

## Context Manager (Recommended)

```python
async with UnifiedMCPClient() as client:
    result = await client.search("query")
    print(result)
# Automatic cleanup
```

## Testing Your Setup

```python
import asyncio
from enhanced_agent.src.unified_mcp_client import UnifiedMCPClient

async def test():
    client = UnifiedMCPClient()

    # Test 1: List servers
    print("Available servers:", client.list_enabled_servers())

    # Test 2: Get routing hints
    hints = client.get_routing_hints()
    print("Strategies:", hints["strategies"])

    # Test 3: Simple search
    result = await client.search("test query")
    print("Search result:", result[:100])

asyncio.run(test())
```

## Common Issues

### "Config file not found"
**Solution:** Create `enhanced_agent/config/mcp_extended.json` or specify path:
```python
client = UnifiedMCPClient("path/to/config.json")
```

### "Timeout connecting to server"
**Solution:** Check that the server is running (e.g., Ollama) or increase timeout in config

### "API key not configured"
**Solution:** Set environment variable:
```bash
export NEWS_API_KEY="your-key"
```

## Next Steps

1. ✅ **Read Full Guide:** `docs/UNIFIED_MCP_GUIDE.md`
2. ✅ **See Examples:** `enhanced_agent/src/ui_integration_example.py`
3. ✅ **Run Tests:** `pytest tests/unit/test_unified_mcp.py -v`
4. ✅ **Check Summary:** `UNIFIED_MCP_SUMMARY.md`
5. ✅ **Migrate:** `UNIFIED_MCP_MIGRATION.md`

## Help & Support

- **Documentation:** `docs/UNIFIED_MCP_GUIDE.md`
- **Examples:** `enhanced_agent/src/ui_integration_example.py`
- **Tests:** `tests/unit/test_unified_mcp.py`
- **API Reference:** See source code docstrings

## Quick Reference

```python
# Import
from enhanced_agent.src.unified_mcp_client import UnifiedMCPClient
from enhanced_agent.src.mcp_config import RoutingStrategy

# Initialize
client = UnifiedMCPClient()

# Search (auto)
result = await client.search("query")

# Search (manual)
result = await client.search("query", servers=["server1"])

# Search (multi)
results = await client.search("query", strategy=RoutingStrategy.MULTI)

# List servers
servers = client.list_enabled_servers()

# Get routing hints
hints = client.get_routing_hints()

# Context manager
async with UnifiedMCPClient() as client:
    result = await client.search("query")
```

---

**Ready to go!** Start with the basic usage example and explore from there. 🚀
