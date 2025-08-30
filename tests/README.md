# Tests Directory

This directory contains all test files for the OMD project, organized by test type and functionality.

## Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared pytest fixtures and configuration
├── README.md               # This file
├── unit/                   # Unit tests for individual components
│   ├── __init__.py
│   ├── test_enhanced_agent.py     # Tests for enhanced agent functionality
│   └── test_dspy_standalone.py    # Standalone DSPy module tests
└── integration/            # Integration tests for system interactions
    ├── __init__.py
    ├── test_dspy_integration.py          # DSPy+MCP+OpenManus integration
    ├── test_integration.py               # General integration tests
    ├── test_multi_mcp.py                 # Multi-server MCP testing
    └── test_enhanced_agent_integration.py # Enhanced agent with OpenManus
```

## Running Tests

### Using the Test Runner Script
```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py unit

# Run only integration tests
python run_tests.py integration

# Run with coverage
python run_tests.py --coverage

# Run fast tests only (exclude slow tests)
python run_tests.py fast
```

### Using pytest directly (with virtual environment)
```bash
# Activate virtual environment first
source virtual/bin/activate

# Run all tests
pytest

# Run unit tests only
pytest -m unit

# Run integration tests only
pytest -m integration

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_enhanced_agent.py

# Run with coverage
pytest --cov=enhanced_agent --cov=OpenManus --cov-report=html
```

### Or use the virtual environment directly
```bash
# Run all tests without activating venv
./virtual/bin/python -m pytest

# Run unit tests only
./virtual/bin/python -m pytest -m unit

# Run integration tests only
./virtual/bin/python -m pytest -m integration
```

## Test Categories

Tests are automatically marked based on their location and content:

- **Unit tests** (`tests/unit/`): Test individual components in isolation
- **Integration tests** (`tests/integration/`): Test system interactions and workflows
- **Slow tests**: Tests marked with `@pytest.mark.slow` or containing "slow" in the name
- **API tests**: Tests that require external API access (marked automatically)

## Test Fixtures

The `conftest.py` file provides shared fixtures for all tests:

- `project_root`: Path to the project root directory
- `mock_openai_api`: Mock OpenAI API calls to avoid actual usage
- `mock_mcp_client`: Mock MCP client for testing without server connections
- `sample_test_queries`: Common test queries for various scenarios
- `mock_dspy_settings`: Mock DSPy settings to avoid configuration issues
- `setup_test_environment`: Automatically sets up test environment

## Best Practices

1. **Use descriptive test names**: Test functions should clearly describe what they test
2. **Use fixtures**: Leverage shared fixtures from `conftest.py` to avoid code duplication
3. **Mock external dependencies**: Use the provided mocks for OpenAI, MCP, etc.
4. **Mark your tests**: Use appropriate pytest markers (`@pytest.mark.unit`, `@pytest.mark.slow`, etc.)
5. **Keep tests isolated**: Each test should be independent and not rely on other tests
6. **Test both success and failure cases**: Include tests for error conditions

## Adding New Tests

1. **Unit tests**: Add to `tests/unit/` directory
2. **Integration tests**: Add to `tests/integration/` directory
3. **Follow naming convention**: `test_*.py` for files, `test_*` for functions
4. **Use appropriate fixtures**: Leverage shared fixtures from `conftest.py`
5. **Add markers**: Use `@pytest.mark.*` decorators as needed

## Configuration

- `pytest.ini`: Main pytest configuration
- `conftest.py`: Shared fixtures and test setup
- Test discovery and execution settings are configured in `pytest.ini`
