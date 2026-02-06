# Quick Start Guide - Running Timer Tests

## Installation

Install test dependencies:

```bash
# Using pip
pip install -r requirements.txt

# Or install test deps specifically
pip install pytest>=8.0.0 pytest-asyncio>=0.23.0 psutil>=5.9.0
```

## Run Tests

```bash
# Navigate to project root
cd /Users/raymondhunter/LocalProjects/10workspaceOct25/omd

# Run all timer tests
pytest tests/unit/test_streamlit_timer.py -v

# Expected output:
# ========================= 13 passed in ~3s =========================
```

## Quick Test Examples

```bash
# Test timer basics
pytest tests/unit/test_streamlit_timer.py::TestStreamlitTimer::test_timer_starts_and_updates -v

# Test cleanup behavior
pytest tests/unit/test_streamlit_timer.py::TestStreamlitTimer::test_timer_stops_cleanly -v

# Skip performance tests (faster)
pytest tests/unit/test_streamlit_timer.py -v -k "not Performance"
```

## Verify Test Quality

```bash
# Check test coverage
pytest tests/unit/test_streamlit_timer.py --cov=enhanced_agent_streamlit --cov-report=term-missing

# Run with detailed output
pytest tests/unit/test_streamlit_timer.py -vv -s
```

## Files Created

1. **Test File**: `tests/unit/test_streamlit_timer.py`
   - 13 comprehensive unit tests
   - 3 test classes (Core, Integration, Performance)
   - ~400 lines of test code

2. **Documentation**: 
   - `tests/unit/TEST_TIMER_README.md` - Detailed test docs
   - `TIMER_FEATURE_SUMMARY.md` - Feature overview

3. **Dependencies**: Updated `requirements.txt` with test packages

## What Gets Tested

✅ Timer starts and updates correctly
✅ Timer stops cleanly
✅ Exception handling and cleanup
✅ Elapsed time accuracy
✅ Message formatting
✅ Async integration
✅ Thread management
✅ Multiple concurrent timers
✅ CPU overhead (<10%)
✅ Memory leak prevention
✅ Streamlit component integration

## Notes

- Tests use mocking to avoid actual Streamlit dependencies
- Performance tests may take slightly longer
- All tests are deterministic and should pass consistently
- Tests are CI/CD ready
