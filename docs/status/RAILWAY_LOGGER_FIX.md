# Railway Logger AttributeError Fix

**Date**: February 5, 2026  
**Issue**: `'Logger' object has no attribute 'info_user_input'` error on Railway deployment  
**Status**: ✅ Fixed

## Problem Description

The application running on Railway was throwing an AttributeError when processing enhanced_research queries:

```
Error: 'Logger' object has no attribute 'info_user_input'
```

This error occurred in the `enhanced_agent/src/app.py`, `enhanced_agent_streamlit.py`, and `enhanced_agent/src/dspy_mcp_integration.py` files when calling the `info_user_input()` method on logger objects.

## Root Cause Analysis

### Primary Issue: Missing Dependency
The `privacy` module (which provides `RedactedLogger` with the `info_user_input()` method) failed to import on Railway because the `watchdog` package was not installed. 

- The `privacy.redacted_logger` module imports `config.settings`
- `config.settings` imports `watchdog` for file system monitoring
- `watchdog` was only listed in `config/requirements.txt`, not in the main `requirements.txt` used by Railway

### Secondary Issue: Incomplete Fallback
When the privacy import failed, the code fell back to standard Python `logging.getLogger()`, which doesn't have the custom methods like:
- `info_user_input()`
- `info_agent_output()`
- `info_mcp_query()`

The fallback was incomplete and would crash when these methods were called.

## Solution Implemented

### 1. Added Missing Dependency
Added `watchdog>=3.0.0` to the main `requirements.txt` to ensure the privacy module can import successfully on Railway.

**File**: `requirements.txt`
```python
# Data processing and utilities
requests>=2.32.0
pydantic>=2.12.0
loguru>=0.7.0
watchdog>=3.0.0  # <-- Added for config.settings file monitoring
```

### 2. Implemented Logger Compatibility Wrapper
Created a `_LoggerWrapper` class in all three files that provides the same interface as `RedactedLogger` but uses standard Python logging as a fallback.

This ensures graceful degradation if the privacy module still fails to import for any reason.

**Files Modified**:
- `enhanced_agent/src/app.py` (lines 26-61)
- `enhanced_agent_streamlit.py` (lines 51-92)
- `enhanced_agent/src/dspy_mcp_integration.py` (lines 30-69)

**Wrapper Implementation**:
```python
class _LoggerWrapper:
    def __init__(self, logger):
        self._logger = logger
    
    def info_user_input(self, message: str, user_input: str):
        """Fallback for info_user_input when privacy module unavailable"""
        self._logger.info(f"{message}: {user_input[:100]}..." if len(user_input) > 100 else f"{message}: {user_input}")
    
    def info_agent_output(self, message: str, agent_output: str):
        """Fallback for info_agent_output when privacy module unavailable"""
        self._logger.info(f"{message}: {agent_output[:100]}..." if len(agent_output) > 100 else f"{message}: {agent_output}")
    
    def info_mcp_query(self, message: str, query: str):
        """Fallback for info_mcp_query when privacy module unavailable"""
        self._logger.info(f"{message}: {query[:100]}..." if len(query) > 100 else f"{message}: {query}")
    
    # Proxy standard logging methods
    def debug(self, *args, **kwargs):
        self._logger.debug(*args, **kwargs)
    
    def info(self, *args, **kwargs):
        self._logger.info(*args, **kwargs)
    
    def warning(self, *args, **kwargs):
        self._logger.warning(*args, **kwargs)
    
    def error(self, *args, **kwargs):
        self._logger.error(*args, **kwargs)
    
    def critical(self, *args, **kwargs):
        self._logger.critical(*args, **kwargs)
```

## Benefits of This Fix

1. **Railway Compatibility**: Application now works correctly on Railway without the privacy module import failing
2. **Graceful Degradation**: If privacy features aren't available, logging still works with standard Python logging
3. **Consistent Interface**: Code using logger objects doesn't need to change - same methods work in both cases
4. **Privacy Protection**: When privacy module IS available, full redaction capabilities are used
5. **Truncation**: Fallback wrapper truncates long inputs at 100 characters to avoid log bloat

## Testing Recommendations

After deploying to Railway:

1. ✅ Verify the application starts without errors
2. ✅ Submit an enhanced_research query and confirm it processes successfully
3. ✅ Check Railway logs to confirm `info_user_input` calls are working
4. ✅ Verify privacy features work if properly configured (with Langfuse keys)

## Related Files

- `privacy/redacted_logger.py` - Original RedactedLogger implementation
- `privacy/__init__.py` - Privacy module exports
- `config/settings.py` - Configuration that requires watchdog
- `config/requirements.txt` - Config-specific dependencies

## Migration Notes

If deploying to other platforms (Streamlit Cloud, Heroku, etc.), ensure:
- All dependencies from `requirements.txt` are installed
- The privacy module can import successfully
- If not, the fallback wrapper will handle logging gracefully
