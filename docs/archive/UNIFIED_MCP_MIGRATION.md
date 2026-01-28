# Unified MCP Client Migration Checklist

## Overview

This document provides a step-by-step checklist for migrating to the unified MCP client system.

## Pre-Migration Checklist

- [ ] Review `UNIFIED_MCP_SUMMARY.md` for overview
- [ ] Review `docs/UNIFIED_MCP_GUIDE.md` for detailed documentation
- [ ] Backup existing configuration files
- [ ] Identify all code using old MCP clients

## Configuration Migration

### Step 1: Create Unified Configuration

- [ ] Create `enhanced_agent/config/mcp_extended.json` (if not exists)
- [ ] Copy server configurations from old configs
- [ ] Add required fields:
  - [ ] `type` for each server
  - [ ] `enabled` flag for each server
  - [ ] `capabilities` lists
  - [ ] `description` strings
- [ ] Add routing configuration:
  - [ ] `server_selection_strategy` (auto/manual/multi)
  - [ ] `fallback_servers` list
  - [ ] `routing_rules` dict
- [ ] Convert API keys to environment variables:
  - [ ] Replace hardcoded keys with `${ENV_VAR}` syntax
  - [ ] Set environment variables in `.env` or system

### Step 2: Validate Configuration

```bash
# Test configuration loading
python -c "
from enhanced_agent.src.mcp_config import load_mcp_config
config = load_mcp_config()
print('✅ Configuration loaded successfully')
print(f'Servers: {list(config.servers.keys())}')
print(f'Default: {config.default_server}')
print(f'Strategy: {config.server_selection_strategy}')
"
```

- [ ] Configuration loads without errors
- [ ] All servers are listed correctly
- [ ] Warnings about missing API keys are acceptable (can be set later)

## Code Migration

### Step 3: Update Imports

#### Old: Basic MCP Client
```python
from enhanced_agent.src.mcp_client import MCPClient
```

#### New: Unified MCP Client
```python
from enhanced_agent.src.unified_mcp_client import UnifiedMCPClient
```

---

#### Old: Enhanced MCP Client
```python
from enhanced_agent.src.enhanced_mcp_client import EnhancedMCPClient
```

#### New: Unified MCP Client
```python
from enhanced_agent.src.unified_mcp_client import UnifiedMCPClient
```

---

#### Old: DSPy Integration
```python
from enhanced_agent.src.dspy_mcp_integration import DSPyMCPIntegration
```

#### New: Unified Integration (Recommended)
```python
from enhanced_agent.src.unified_integration import UnifiedDSPyMCPIntegration
```

**Note:** Old `DSPyMCPIntegration` still works but doesn't have routing hints API.

### Step 4: Update Client Initialization

#### Old: Basic Client
```python
client = MCPClient("config/mcp.json")
```

#### New: Unified Client
```python
# Auto-finds config
client = UnifiedMCPClient()

# Or specify path
client = UnifiedMCPClient("path/to/config.json")

# Or pass config object
from enhanced_agent.src.mcp_config import load_mcp_config
config = load_mcp_config()
client = UnifiedMCPClient(config)
```

---

#### Old: Enhanced Client
```python
client = EnhancedMCPClient("config/mcp_extended.json")
```

#### New: Unified Client
```python
client = UnifiedMCPClient()  # Auto-finds mcp_extended.json
```

### Step 5: Update Search Calls

#### Old: Basic Client
```python
# Sync call (old)
result = client.search("query", server="llama-mcp")

# Async call (old)
result = await client.search("query", server="llama-mcp")
```

#### New: Unified Client
```python
# Async call (all methods are async)
result = await client.search("query", servers=["llama-mcp"])

# Auto routing
result = await client.search("query")  # Uses routing rules

# Multi-server
from enhanced_agent.src.mcp_config import RoutingStrategy
result = await client.search("query", strategy=RoutingStrategy.MULTI)
# Returns: {"server1": "result1", "server2": "result2"}
```

---

#### Old: Enhanced Client
```python
# Auto-select (sync)
results = client.search("query")

# Manual select (sync)
results = client.search("query", servers=["server1", "server2"])

# Single server (sync)
result = client.search_single_server("query", "server1")
```

#### New: Unified Client
```python
# Auto-select (async)
result = await client.search("query")

# Manual select (async)
results = await client.search("query", servers=["server1", "server2"])

# Single server (async) - internal method, use search with single server
result = await client.search("query", servers=["server1"])
```

### Step 6: Update Integration Usage

#### Old: DSPy Integration
```python
integration = DSPyMCPIntegration(
    mcp_config_path="config/mcp.json",
    llm_model="gpt-3.5-turbo"
)

# No routing hints available
```

#### New: Unified Integration
```python
integration = UnifiedDSPyMCPIntegration(
    llm_model="gpt-3.5-turbo"  # Auto-finds config
)

# Get routing hints for UI
hints = integration.get_routing_hints()
servers = integration.get_available_servers()
```

## UI Migration

### Step 7: Update UI Controls

#### Create UI Integration Helper
```python
from enhanced_agent.src.ui_integration_example import UIIntegrationHelper

helper = UIIntegrationHelper(integration)
```

#### Replace Hardcoded Server Lists
```python
# OLD: Hardcoded
servers = ["llama-mcp", "web-search", "wikipedia"]

# NEW: From backend
server_choices = helper.get_server_choices()
servers = [s["name"] for s in server_choices]
```

#### Replace Hardcoded Strategies
```python
# OLD: Hardcoded
strategies = ["auto", "manual", "multi"]

# NEW: From backend
strategy_choices = helper.get_strategy_choices()
strategies = [s["value"] for s in strategy_choices]
```

#### Map UI Controls to Backend
```python
# Streamlit example
selected_strategy = st.radio("Mode:", strategies)
selected_servers = st.multiselect("Servers:", servers)

# Backend call uses same values
result = await integration.research(
    query=query,
    servers=selected_servers if selected_servers else None,
    strategy=RoutingStrategy(selected_strategy)
)
```

### Step 8: Update API Endpoints

#### FastAPI Example
```python
from fastapi import FastAPI
from enhanced_agent.src.ui_integration_example import create_fastapi_endpoints

app = FastAPI()
create_fastapi_endpoints(app, integration)

# Endpoints created:
# GET  /api/routing-hints - Configuration for UI
# GET  /api/servers - Available servers
# POST /api/search - Execute search with routing
# POST /api/quick-search - Fast search without DSPy
```

## Testing

### Step 9: Run Unit Tests

```bash
# Install test dependencies if needed
python -m pip install pytest pytest-asyncio

# Run unified MCP tests
pytest tests/unit/test_unified_mcp.py -v --asyncio-mode=auto

# Expected: 28 passed
```

- [ ] All tests pass
- [ ] No unexpected failures

### Step 10: Integration Testing

```bash
# Test basic search
python -c "
import asyncio
from enhanced_agent.src.unified_mcp_client import UnifiedMCPClient

async def test():
    async with UnifiedMCPClient() as client:
        result = await client.search('test query')
        print('✅ Basic search works')
        print(f'Result: {result[:100]}...')

asyncio.run(test())
"
```

- [ ] Basic search works
- [ ] Returns expected result format

```bash
# Test DSPy integration
python -c "
import asyncio
from enhanced_agent.src.unified_integration import UnifiedDSPyMCPIntegration

async def test():
    integration = UnifiedDSPyMCPIntegration()
    hints = integration.get_routing_hints()
    print('✅ Routing hints work')
    print(f'Available servers: {len(hints[\"available_servers\"])}')
    print(f'Strategies: {hints[\"strategies\"]}')

asyncio.run(test())
"
```

- [ ] Routing hints API works
- [ ] Returns expected structure

## Deployment

### Step 11: Environment Variables

- [ ] Set all required API keys as environment variables
- [ ] Test loading with production environment
- [ ] Verify no hardcoded secrets remain

```bash
# Example .env file
export NEWS_API_KEY="your-key"
export GITHUB_TOKEN="your-token"
export WEATHER_API_KEY="your-key"
```

### Step 12: Update Documentation

- [ ] Update project README with new usage
- [ ] Update API documentation
- [ ] Update deployment guides
- [ ] Add migration notes to CHANGELOG

### Step 13: Deprecation Plan

- [ ] Mark old MCP clients as deprecated (add warnings)
- [ ] Set deprecation timeline
- [ ] Communicate to team/users

#### Example Deprecation Warning
```python
# In old mcp_client.py
import warnings

class MCPClient:
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "MCPClient is deprecated. Use UnifiedMCPClient instead. "
            "See UNIFIED_MCP_GUIDE.md for migration instructions.",
            DeprecationWarning,
            stacklevel=2
        )
        # ... rest of init
```

## Verification

### Step 14: Final Checks

- [ ] All imports updated
- [ ] All async/await patterns correct
- [ ] All tests passing
- [ ] UI controls map to backend
- [ ] No hardcoded server lists
- [ ] No hardcoded routing strategies
- [ ] Environment variables set
- [ ] Documentation updated
- [ ] Team trained on new system

## Rollback Plan

If issues arise during migration:

1. **Keep old code temporarily**: Don't delete old MCP clients immediately
2. **Feature flag**: Use environment variable to toggle between old/new
   ```python
   USE_UNIFIED_MCP = os.getenv("USE_UNIFIED_MCP", "false").lower() == "true"

   if USE_UNIFIED_MCP:
       from enhanced_agent.src.unified_mcp_client import UnifiedMCPClient as Client
   else:
       from enhanced_agent.src.mcp_client import MCPClient as Client
   ```
3. **Monitor metrics**: Track success rates, response times, errors
4. **Quick revert**: Switch feature flag if needed

## Support Resources

- **Documentation**: `docs/UNIFIED_MCP_GUIDE.md`
- **Examples**: `enhanced_agent/src/ui_integration_example.py`
- **Tests**: `tests/unit/test_unified_mcp.py`
- **Summary**: `UNIFIED_MCP_SUMMARY.md`

## Success Criteria

Migration is complete when:

- ✅ All code uses unified MCP client
- ✅ All tests pass
- ✅ UI controls populated from backend API
- ✅ No UI/backend drift
- ✅ Environment variables properly configured
- ✅ Documentation updated
- ✅ Team trained

## Timeline Estimate

- **Small project** (1-2 files): 1-2 hours
- **Medium project** (3-10 files): 4-8 hours
- **Large project** (10+ files): 1-3 days

Most time is spent on:
1. Configuration migration (30%)
2. Code updates (40%)
3. Testing and validation (20%)
4. Documentation (10%)

## Post-Migration

After successful migration:

1. **Monitor**: Track usage patterns, errors, performance
2. **Optimize**: Adjust routing rules based on usage
3. **Extend**: Add new server types as needed
4. **Clean up**: Remove old MCP client code after stabilization period
5. **Share**: Document lessons learned for future migrations
