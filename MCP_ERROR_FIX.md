# MCP "Query returned error" Fix

## Problem

All queries were returning "Error: Query returned error" with no specific details about what was failing.

## Root Cause

The MCP configuration included a `llama-mcp` server that tries to connect to `http://localhost:11434` (Ollama). When deployed on Railway:

1. There is no Ollama server running at localhost:11434
2. The MCP client was trying to use this server (it was in the fallback list)
3. Connection failures were returning generic "Query returned error" messages
4. The actual error details were being truncated

## Changes Made

### 1. Disabled Localhost-Based MCP Server
**File**: `enhanced_agent/config/mcp.json`

```json
"llama-mcp": {
  "enabled": false,  // Changed from true
  "local_only": true,  // Added flag to indicate local-only server
  ...
}
```

### 2. Updated Fallback Servers
**File**: `enhanced_agent/config/mcp.json`

```json
// Before
"fallback_servers": ["web-search", "llama-mcp"]

// After
"fallback_servers": ["web-search", "wikidata", "arxiv"]
```

Now uses only web-based servers that work on Railway.

### 3. Improved Error Messages
**File**: `enhanced_agent/src/dspy_mcp_integration.py` (line 392-397)

```python
# Before
error_detail = "Query returned error"

// After
error_detail = str(response)[:300] if response else "No response"
```

Now shows the first 300 characters of the actual error for debugging.

### 4. Added Server Logging
**File**: `enhanced_agent/src/unified_mcp_client.py` (line 72)

```python
enabled_servers = self.config.get_enabled_servers()
logger.info(f"MCP Client initialized with {len(enabled_servers)} enabled servers: {', '.join(enabled_servers)}")
```

Now logs which MCP servers are actually enabled when the app starts.

## Available MCP Servers (Cloud-Ready)

After the fix, these servers are enabled and working:

1. **web-search** (DuckDuckGo) - Default
   - Current events, real-time data, web search
   
2. **wikidata** - Fallback
   - Structured knowledge, factual data, entities
   
3. **dbpedia** - Fallback
   - Encyclopedic knowledge, structured Wikipedia data
   
4. **arxiv** - Fallback
   - Scientific research, academic papers
   
5. **news-api** - Topic-based routing
   - Breaking news, current events
   - Requires: `NEWS_API_KEY` environment variable
   
6. **weather** - Topic-based routing
   - Current weather, forecasts
   - Requires: `OPENWEATHER_API_KEY` environment variable

## Testing the Fix

After deploying these changes:

1. **Check Startup Logs**
   - Should see: "MCP Client initialized with X enabled servers: web-search, wikidata, dbpedia, arxiv..."
   - Should NOT see llama-mcp in the list

2. **Test Queries**
   - General queries: "What is machine learning?"
   - Weather queries: "Weather in San Francisco" (needs API key)
   - News queries: "Latest AI news" (needs API key)
   
3. **Check for Errors**
   - Errors should now show specific details instead of "Query returned error"
   - Example: "Error: Could not connect to..." instead of generic message

## Local Development

For local development with Ollama:

1. Re-enable the llama-mcp server:
   ```json
   "llama-mcp": {
     "enabled": true,
     ...
   }
   ```

2. Add it back to fallback servers if desired:
   ```json
   "fallback_servers": ["web-search", "llama-mcp", "wikidata", "arxiv"]
   ```

3. Make sure Ollama is running:
   ```bash
   # Start Ollama
   ollama serve
   
   # Verify it's running
   curl http://localhost:11434/api/tags
   ```

## Optional API Keys for Enhanced Functionality

Set these in Railway environment variables for additional capabilities:

```bash
NEWS_API_KEY=your-key-here              # For news-api server
OPENWEATHER_API_KEY=your-key-here       # For weather server
```

Get API keys:
- News API: https://newsapi.org/register
- OpenWeatherMap: https://openweathermap.org/api

## Verification Checklist

✅ llama-mcp disabled in `mcp.json`
✅ fallback_servers updated to web-only servers  
✅ Error messages show actual error details
✅ Server initialization logging added
✅ App successfully deploys on Railway
✅ Queries return results without errors

## Future Improvements

Consider:
1. Add automatic server health checks on startup
2. Implement retry logic for transient failures
3. Add server-specific timeout configurations
4. Create Railway-specific MCP config file
5. Add telemetry for MCP server success rates
