import pytest
import requests
from playwright.sync_api import sync_playwright

from app.config import Config
# from mcp_client import MCPClient  # Commented out as this may not exist yet


# @pytest.fixture
# def mcp_client():
#     """Creates an MCP client instance for testing."""
#     return MCPClient("mcp.json")


@pytest.fixture
def config():
    """Creates a config instance for testing."""
    return Config()


def test_llama_mcp_connection():
    """Tests Llama MCP (Ollama) connection."""
    response = requests.get("http://localhost:11434/api/version")
    assert response.status_code == 200, "Ollama server is not running"
    version_info = response.json()
    assert version_info, "Could not get Ollama version info"


# def test_mcp_client_initialization(mcp_client):
#     """Tests MCP client initialization."""
#     assert mcp_client.default_server, "Default server not set"
#     servers = mcp_client.list_servers()
#     assert servers, "No MCP servers configured"
#     assert mcp_client.default_server in servers, "Default server not in server list"


def test_playwright_connection():
    """Tests Playwright browser automation."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:3000")
        assert page.url == "http://localhost:3000"
        browser.close()


def test_mcp_config_loading(config):
    """Tests MCP configuration loading."""
    assert config.llm, "LLM configuration not loaded"
    assert config.llm.api_type == "ollama", "Expected Ollama API type"
    assert config.llm.model == "gemma3", "Expected Gemma3 model" 