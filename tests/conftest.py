"""
Pytest configuration and shared fixtures for the OMD project tests.

This file contains shared test fixtures, configurations, and utilities
that can be used across all test files in the project.
"""

import pytest
import asyncio
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return PROJECT_ROOT


@pytest.fixture
def mock_openai_api():
    """Mock OpenAI API calls to avoid actual API usage during tests."""
    with patch('dspy.OpenAI') as mock_openai:
        mock_instance = Mock()
        mock_openai.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_mcp_client():
    """Mock MCP client for testing without actual server connections."""
    with patch('enhanced_agent.src.mcp_client.MCPClient') as mock_client:
        mock_instance = Mock()
        mock_instance.list_servers.return_value = ['llama-mcp', 'test-server']
        mock_instance.get_server_info.return_value = {
            'url': 'http://localhost:11434',
            'capabilities': ['search', 'analyze']
        }
        mock_instance.search_single_server.return_value = "Mock search result"
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_test_queries():
    """Provide common test queries for various test scenarios."""
    return [
        "What is machine learning?",
        "How does photosynthesis work?", 
        "What are the latest developments in quantum computing?",
        "Current weather in New York",
        "TSLA stock price"
    ]


@pytest.fixture
def mock_dspy_settings():
    """Mock DSPy settings to avoid configuration issues in tests."""
    with patch('dspy.settings') as mock_settings:
        mock_settings.configure = Mock()
        yield mock_settings


@pytest.fixture
def disable_logging():
    """Disable logging during tests to reduce noise."""
    import logging
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Automatically set up test environment for each test."""
    # Ensure we're in the project root
    original_cwd = os.getcwd()
    os.chdir(PROJECT_ROOT)
    
    # Set test environment variable
    os.environ['TESTING'] = '1'
    
    yield
    
    # Cleanup
    os.chdir(original_cwd)
    os.environ.pop('TESTING', None)


@pytest.fixture
def mock_enhanced_agent():
    """Mock the enhanced agent for integration tests."""
    async def mock_run_enhanced_agent(query):
        return f"Mock response for query: {query}"
    
    with patch('enhanced_agent.src.app.run_enhanced_agent', side_effect=mock_run_enhanced_agent):
        yield mock_run_enhanced_agent


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_api: marks tests that require external API access"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Mark tests in unit/ directory as unit tests
        if "tests/unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Mark tests in integration/ directory as integration tests  
        elif "tests/integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Mark tests that contain "slow" in name as slow
        if "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)
            
        # Mark tests that might require API access
        if any(keyword in item.name.lower() for keyword in ['api', 'openai', 'external']):
            item.add_marker(pytest.mark.requires_api)
