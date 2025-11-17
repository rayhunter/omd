# Async-Friendly MCP Implementation

## Overview

This document describes the implementation of async-friendly MCP (Model Context Protocol) access with improved concurrency control and performance.

## Key Changes

### 1. Replaced Blocking HTTP with httpx.AsyncClient

**File**: `enhanced_agent/src/mcp_client.py`

- **Removed**: `requests` library (blocking synchronous HTTP)
- **Added**: `httpx` library with `AsyncClient` for non-blocking HTTP operations
- **Benefits**:
  - Non-blocking I/O operations
  - Better performance with concurrent requests
  - Native async/await support
  - Proper timeout handling

**Example**:
```python
# Before (blocking)
response = requests.post(url, json=payload, timeout=60)

# After (async)
async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
    response = await client.post(url, json=payload)
```

### 2. Added ThreadPoolExecutor for Blocking SDK Operations

**File**: `enhanced_agent/src/mcp_client.py:18-21,127-142`

For libraries that don't support async (e.g., some Ollama SDKs), we offload blocking calls to a thread pool executor:

```python
# Thread pool executor for blocking operations
self._executor = ThreadPoolExecutor(max_workers=4)

async def _run_blocking_operation(self, func, *args, **kwargs):
    """Run blocking SDK call in thread pool executor"""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(self._executor, lambda: func(*args, **kwargs))
```

**Usage**:
```python
# For blocking SDK calls
result = await self._run_blocking_operation(blocking_sdk_function, arg1, arg2)
```

### 3. Implemented Semaphore-Based Concurrency Control

**File**: `enhanced_agent/src/dspy_mcp_integration.py:87-91,233-291`

Added a semaphore to control the maximum number of concurrent MCP queries:

```python
# Configuration
self.config = {
    'max_concurrent_queries': 3,  # Max concurrent MCP queries
}

# Semaphore for rate limiting
self._mcp_semaphore = asyncio.Semaphore(self.config['max_concurrent_queries'])
```

**Usage in gather_information**:
```python
async def _query_with_semaphore(term: str, index: int) -> Dict[str, Any]:
    async with self._mcp_semaphore:  # Rate limiting
        response = await self.mcp_client.search(term)
        # Process response...

# Execute all queries concurrently with rate limiting
results = await asyncio.gather(*query_tasks, return_exceptions=True)
```

### 4. Added Proper Timeout Handling

**Files**:
- `enhanced_agent/src/mcp_client.py:72,81-89,101,109-117`

All HTTP operations now have explicit timeout configuration:

```python
# Configure timeout
timeout = httpx.Timeout(config.get("timeout", 60.0))

# Use in requests
async with httpx.AsyncClient(timeout=timeout) as client:
    response = await client.post(url, json=payload)
```

**Error Handling**:
```python
except httpx.TimeoutException as e:
    return f"Error: Timeout connecting to server."
except httpx.HTTPError as e:
    return f"Error: Could not connect to server."
```

### 5. Async Context Manager Support

**File**: `enhanced_agent/src/mcp_client.py:144-159`

Added proper resource cleanup with async context manager:

```python
async def __aenter__(self):
    """Async context manager entry."""
    return self

async def __aexit__(self, exc_type, exc_val, exc_tb):
    """Async context manager exit."""
    await self.close()

async def close(self):
    """Close HTTP client and thread pool executor."""
    if self._http_client:
        await self._http_client.aclose()
    self._executor.shutdown(wait=True)
```

**Usage**:
```python
async with MCPClient() as client:
    result = await client.search("query")
# Automatic cleanup on exit
```

### 6. Concurrent Query Execution

**File**: `enhanced_agent/src/dspy_mcp_integration.py:285-291`

The `gather_information` method now executes queries concurrently:

```python
# Create tasks for all queries
query_tasks = [
    _query_with_semaphore(term, i)
    for i, term in enumerate(limited_terms)
]

# Execute concurrently with semaphore-based rate limiting
results = await asyncio.gather(*query_tasks, return_exceptions=True)
```

## Performance Benefits

### Before (Sequential)
```
Query 1: ████████░░░░░░░░░░░░ (2s)
Query 2:         ████████░░░░░░░░░░░░ (2s)
Query 3:                 ████████░░░░░░░░░░░░ (2s)
Total: 6 seconds
```

### After (Concurrent with Semaphore)
```
Query 1: ████████░░░░░░░░░░░░ (2s)
Query 2: ████████░░░░░░░░░░░░ (2s) - concurrent
Query 3: ████████░░░░░░░░░░░░ (2s) - concurrent
Total: 2 seconds (3x faster!)
```

## Configuration

### MCP Client Timeout Configuration

Edit `enhanced_agent/config/mcp.json`:

```json
{
  "servers": {
    "llama-mcp": {
      "url": "http://localhost:11434",
      "timeout": 60,  // Timeout in seconds
      "model": "gemma2:2b"
    }
  }
}
```

### Concurrency Configuration

In `enhanced_agent/src/dspy_mcp_integration.py`:

```python
self.config = {
    'max_mcp_queries': 3,       // Total queries per session
    'max_concurrent_queries': 3, // Max concurrent queries
}
```

## Testing

### Validation Script

Run the validation script to verify the implementation:

```bash
python test_async_validation.py
```

This validates:
- ✅ All async methods are properly defined
- ✅ httpx is used instead of requests
- ✅ ThreadPoolExecutor is available
- ✅ Semaphore-based concurrency control
- ✅ asyncio.gather for concurrent execution
- ✅ Proper dependencies in pyproject.toml

### Integration Tests

```bash
# Test async MCP client
python tests/integration/test_multi_mcp.py

# Note: Requires Ollama running on localhost:11434
ollama serve
ollama pull gemma2:2b
```

## Dependencies

Updated `enhanced_agent/pyproject.toml`:

```toml
dependencies = [
    "httpx>=0.27.0",      # Async HTTP client (replaces requests)
    "dspy-ai>=2.3.3",
    "openmanus",
    "streamlit>=1.28.0",
]
```

## Migration Guide

### For Code Using MCPClient

**Before**:
```python
from enhanced_agent.src.mcp_client import MCPClient

client = MCPClient()
result = client.search("query")  # Blocking call
```

**After**:
```python
from enhanced_agent.src.mcp_client import MCPClient

async with MCPClient() as client:
    result = await client.search("query")  # Async call
```

### For Code Using DSPyMCPIntegration

**Before**:
```python
integration = DSPyMCPIntegration()
# gather_information was blocking
info = integration.gather_information(search_terms)
```

**After**:
```python
integration = DSPyMCPIntegration()
# gather_information is now async with concurrent execution
info = await integration.gather_information(search_terms)
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│ DSPyMCPIntegration                                      │
│  - Semaphore (max_concurrent_queries=3)                │
│  - asyncio.gather for parallel execution               │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│ MCPClient (Async)                                       │
│  - httpx.AsyncClient (non-blocking HTTP)               │
│  - ThreadPoolExecutor (for blocking SDKs)              │
│  - Async context manager (__aenter__/__aexit__)       │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│ External Services                                       │
│  - Ollama (http://localhost:11434)                     │
│  - Playwright MCP Server                                │
│  - Other MCP-compatible services                        │
└─────────────────────────────────────────────────────────┘
```

## Key Implementation Details

### Request Timeout Flow

1. Configure timeout in `mcp.json`
2. Create `httpx.Timeout` object with configured value
3. Pass to `AsyncClient` constructor
4. Catch `httpx.TimeoutException` for graceful handling

### Concurrency Control Flow

1. Create semaphore with `max_concurrent_queries` limit
2. Wrap each query in `async with self._mcp_semaphore:`
3. Use `asyncio.gather(*tasks)` to execute concurrently
4. Semaphore automatically limits concurrent executions

### Error Handling Strategy

- **Network errors**: Return error message, don't crash
- **Timeouts**: Catch `httpx.TimeoutException`, return error
- **Concurrent failures**: Use `return_exceptions=True` in gather
- **Graceful degradation**: Continue with partial results

## Performance Tuning

### Adjusting Concurrency

```python
# Lower concurrency (more conservative)
self.config = {'max_concurrent_queries': 2}

# Higher concurrency (more aggressive)
self.config = {'max_concurrent_queries': 5}
```

### Adjusting Timeouts

```python
# Shorter timeout (fail fast)
"timeout": 30  # 30 seconds

# Longer timeout (wait longer)
"timeout": 120  # 2 minutes
```

## Best Practices

1. **Always use async context manager**: Ensures proper cleanup
2. **Handle exceptions gracefully**: Don't let one failure crash everything
3. **Configure appropriate timeouts**: Balance between waiting and failing fast
4. **Monitor semaphore limits**: Adjust based on server capacity
5. **Use executor for blocking operations**: Keep event loop responsive

## Future Enhancements

- [ ] Add connection pooling for better performance
- [ ] Implement retry logic with exponential backoff
- [ ] Add circuit breaker pattern for failing services
- [ ] Implement request/response caching
- [ ] Add metrics and monitoring hooks
- [ ] Support for streaming responses

## References

- [httpx Documentation](https://www.python-httpx.org/)
- [asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor)
- [Semaphore Pattern](https://docs.python.org/3/library/asyncio-sync.html#asyncio.Semaphore)
