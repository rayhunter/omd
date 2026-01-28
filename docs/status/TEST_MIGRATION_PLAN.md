# Test Files Migration Plan

## Overview
This document outlines the plan to move all `test_*.py` files from the project root into the organized `tests/` directory structure.

## Current State
- **22 test files** in root directory
- **Organized structure** already exists in `tests/unit/` and `tests/integration/`
- **pytest.ini** configured to look in `tests/` folder by default

## Migration Strategy

### Step 1: Categorize Test Files

#### Integration Tests (move to `tests/integration/`)
These test interactions between components or external services:
- `test_mcp_integration.py` - MCP integration testing
- `test_async_mcp.py` - Async MCP client integration
- `test_async_validation.py` - Async validation integration
- `test_arxiv_integration.py` - ArXiv API integration
- `test_duckduckgo_integration.py` - DuckDuckGo integration
- `test_news_weather.py` - News/weather API integration
- `test_wikidata_dbpedia.py` - Wikidata/DBpedia integration
- `test_weather_mcp.py` - Weather MCP integration
- `test_dspy_langfuse.py` - DSPy + Langfuse integration
- `test_privacy_integration.py` - Privacy features integration
- `test_session_tracking.py` - Session tracking integration
- `test_langfuse_comprehensive.py` - Comprehensive Langfuse integration
- `test_langfuse_api.py` - Langfuse API integration
- `test_langfuse_send.py` - Langfuse send operations
- `test_mcp_servers_display.py` - MCP server display integration

#### Unit Tests (move to `tests/unit/`)
These test individual components in isolation:
- `test_langfuse_simple.py` - Simple Langfuse unit test
- `test_langfuse_config.py` - Langfuse configuration unit test
- `test_mcp_simple.py` - Simple MCP unit test
- `test_mcp_default_server.py` - MCP default server unit test
- `test_dspy_robustness.py` - DSPy robustness unit test
- `test_dspy_robustness_simple.py` - Simple DSPy robustness test
- `test_package_imports.py` - Package import unit test
- `test_event_loop_reuse.py` - Event loop unit test

### Step 2: Handle Import Paths

After moving files, you may need to update imports. Most files use:
```python
# Current (in root):
from langfuse_integration import langfuse_manager
from enhanced_agent.src.app import ...

# After move (in tests/):
# Same imports should work if project root is in PYTHONPATH
# Or use relative imports from tests/
```

### Step 3: Update pytest Configuration

The `pytest.ini` already has:
```ini
testpaths = tests
```

This means pytest will automatically discover tests in the `tests/` directory.

### Step 4: Update run_tests.py

The `run_tests.py` script already expects tests in `tests/` folder, so no changes needed.

## Migration Commands

### Option 1: Manual Move (Recommended for Review)

```bash
# Integration tests
mv test_mcp_integration.py tests/integration/
mv test_async_mcp.py tests/integration/
mv test_async_validation.py tests/integration/
mv test_arxiv_integration.py tests/integration/
mv test_duckduckgo_integration.py tests/integration/
mv test_news_weather.py tests/integration/
mv test_wikidata_dbpedia.py tests/integration/
mv test_weather_mcp.py tests/integration/
mv test_dspy_langfuse.py tests/integration/
mv test_privacy_integration.py tests/integration/
mv test_session_tracking.py tests/integration/
mv test_langfuse_comprehensive.py tests/integration/
mv test_langfuse_api.py tests/integration/
mv test_langfuse_send.py tests/integration/
mv test_mcp_servers_display.py tests/integration/

# Unit tests
mv test_langfuse_simple.py tests/unit/
mv test_langfuse_config.py tests/unit/
mv test_mcp_simple.py tests/unit/
mv test_mcp_default_server.py tests/unit/
mv test_dspy_robustness.py tests/unit/
mv test_dspy_robustness_simple.py tests/unit/
mv test_package_imports.py tests/unit/
mv test_event_loop_reuse.py tests/unit/
```

### Option 2: Automated Script

I can create a Python script to:
1. Move files to appropriate directories
2. Update import paths if needed
3. Verify all tests still run

## Verification Steps

After migration:

1. **Run all tests**:
   ```bash
   pytest tests/
   ```

2. **Run unit tests only**:
   ```bash
   pytest tests/unit/
   ```

3. **Run integration tests only**:
   ```bash
   pytest tests/integration/
   ```

4. **Check for broken imports**:
   ```bash
   python -m pytest tests/ --collect-only
   ```

## Potential Issues & Solutions

### Issue 1: Import Path Problems
**Problem**: Tests in `tests/` may not find modules in project root.

**Solution**: 
- Ensure project root is in PYTHONPATH
- Or update imports to use `sys.path` manipulation
- Or use relative imports (if applicable)

### Issue 2: Test Discovery
**Problem**: Some tests might not be discovered by pytest.

**Solution**: 
- Verify `pytest.ini` has correct `testpaths`
- Check that test files follow `test_*.py` naming
- Ensure test functions start with `test_`

### Issue 3: Standalone Scripts
**Problem**: Some files might be meant to run standalone (not via pytest).

**Solution**:
- Keep standalone scripts in root with different naming (e.g., `check_*.py`)
- Or add `if __name__ == "__main__"` blocks that work from `tests/`

## Benefits After Migration

✅ **Cleaner root directory** - Only essential files visible  
✅ **Better organization** - Clear separation of unit vs integration tests  
✅ **Easier discovery** - pytest automatically finds all tests  
✅ **Standard structure** - Follows Python testing best practices  
✅ **Better CI/CD** - Standard test paths for automation  
✅ **Easier maintenance** - Related tests grouped together  

## Rollback Plan

If issues arise:
1. Git makes it easy to revert: `git checkout HEAD -- test_*.py`
2. Or move files back manually
3. Tests in root will still work if pytest is run from root

## Next Steps

1. ✅ Review this plan
2. ⏳ Execute migration (manual or automated)
3. ⏳ Run verification tests
4. ⏳ Update any CI/CD configurations if needed
5. ⏳ Update documentation if test locations are referenced

---

**Status**: Ready for execution  
**Estimated Time**: 15-30 minutes  
**Risk Level**: Low (easily reversible)

