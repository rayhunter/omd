"""
Unit tests for Unified MCP Client

Tests cover:
- Configuration loading and validation
- Server selection and routing
- Query execution
- Error handling
- API compatibility
"""

import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import httpx

from enhanced_agent.src.mcp_config import (
    MCPConfig,
    ServerConfig,
    ServerType,
    RoutingStrategy,
    MCPConfigLoader,
    load_mcp_config
)
from enhanced_agent.src.unified_mcp_client import UnifiedMCPClient


# ==================== Fixtures ====================

@pytest.fixture
def sample_config_dict():
    """Sample configuration dictionary"""
    return {
        "servers": {
            "test-ollama": {
                "type": "ollama",
                "url": "http://localhost:11434",
                "model": "llama2",
                "enabled": True,
                "timeout": 30,
                "capabilities": ["general_knowledge"]
            },
            "test-web": {
                "type": "web_search",
                "url": "https://api.duckduckgo.com",
                "enabled": True,
                "timeout": 30,
                "capabilities": ["web_search", "current_events"]
            },
            "test-disabled": {
                "type": "wikipedia",
                "url": "https://en.wikipedia.org",
                "enabled": False,
                "timeout": 30,
                "capabilities": ["encyclopedic_knowledge"]
            }
        },
        "default_server": "test-ollama",
        "server_selection_strategy": "auto",
        "fallback_servers": ["test-ollama", "test-web"],
        "routing_rules": {
            "current_events": ["test-web"],
            "general_knowledge": ["test-ollama"]
        }
    }


@pytest.fixture
def sample_config(sample_config_dict):
    """Sample MCPConfig instance"""
    return MCPConfigLoader._parse_config(sample_config_dict)


@pytest.fixture
def mock_unified_client(sample_config):
    """Mock unified MCP client"""
    return UnifiedMCPClient(sample_config)


@pytest.fixture
def temp_config_file(tmp_path, sample_config_dict):
    """Create temporary config file"""
    config_file = tmp_path / "test_mcp_config.json"
    with open(config_file, 'w') as f:
        json.dump(sample_config_dict, f)
    return str(config_file)


# ==================== Configuration Tests ====================

class TestMCPConfig:
    """Test configuration loading and validation"""

    def test_server_config_creation(self):
        """Test creating ServerConfig from dict"""
        data = {
            "type": "ollama",
            "url": "http://localhost:11434",
            "model": "llama2",
            "enabled": True,
            "timeout": 30,
            "capabilities": ["general_knowledge"]
        }
        config = ServerConfig.from_dict("test-server", data)

        assert config.name == "test-server"
        assert config.type == ServerType.OLLAMA
        assert config.url == "http://localhost:11434"
        assert config.model == "llama2"
        assert config.enabled is True
        assert config.timeout == 30
        assert "general_knowledge" in config.capabilities

    def test_server_config_to_dict(self):
        """Test converting ServerConfig to dict"""
        config = ServerConfig(
            name="test",
            type=ServerType.OLLAMA,
            url="http://localhost:11434",
            model="llama2",
            capabilities=["general_knowledge"]
        )
        data = config.to_dict()

        assert data["name"] == "test"
        assert data["type"] == "ollama"
        assert data["url"] == "http://localhost:11434"
        assert data["model"] == "llama2"

    def test_config_loading_from_file(self, temp_config_file):
        """Test loading config from file"""
        config = MCPConfigLoader.load_from_file(temp_config_file)

        assert isinstance(config, MCPConfig)
        assert "test-ollama" in config.servers
        assert config.default_server == "test-ollama"
        assert config.server_selection_strategy == RoutingStrategy.AUTO

    def test_env_var_substitution(self):
        """Test environment variable substitution"""
        content = '{"api_key": "${TEST_API_KEY}", "url": "http://localhost"}'

        # Without env var
        result = MCPConfigLoader._replace_env_vars(content)
        assert "${TEST_API_KEY}" in result

        # With env var
        import os
        os.environ["TEST_API_KEY"] = "test-key-123"
        result = MCPConfigLoader._replace_env_vars(content)
        assert "test-key-123" in result
        assert "${TEST_API_KEY}" not in result

        del os.environ["TEST_API_KEY"]

    def test_config_validation_missing_url(self):
        """Test validation catches missing required fields"""
        config_dict = {
            "servers": {
                "bad-server": {
                    "type": "ollama"
                    # Missing "url"
                }
            },
            "default_server": "bad-server"
        }

        with pytest.raises(ValueError, match="missing required field 'url'"):
            MCPConfigLoader._parse_config(config_dict)

    def test_config_validation_invalid_type(self):
        """Test validation catches invalid server type"""
        config_dict = {
            "servers": {
                "bad-server": {
                    "type": "invalid_type",
                    "url": "http://localhost"
                }
            },
            "default_server": "bad-server"
        }

        with pytest.raises(ValueError, match="invalid type"):
            MCPConfigLoader._parse_config(config_dict)

    def test_config_validation_invalid_default_server(self):
        """Test validation catches invalid default server"""
        config_dict = {
            "servers": {
                "test-server": {
                    "type": "ollama",
                    "url": "http://localhost"
                }
            },
            "default_server": "non-existent"
        }

        with pytest.raises(ValueError, match="not found in servers list"):
            MCPConfigLoader._parse_config(config_dict)

    def test_get_enabled_servers(self, sample_config):
        """Test getting enabled servers"""
        enabled = sample_config.get_enabled_servers()
        assert "test-ollama" in enabled
        assert "test-web" in enabled
        assert "test-disabled" not in enabled

    def test_get_servers_by_capability(self, sample_config):
        """Test getting servers by capability"""
        web_servers = sample_config.get_servers_by_capability("web_search")
        assert "test-web" in web_servers
        assert "test-ollama" not in web_servers

    def test_get_servers_by_type(self, sample_config):
        """Test getting servers by type"""
        ollama_servers = sample_config.get_servers_by_type(ServerType.OLLAMA)
        assert "test-ollama" in ollama_servers
        assert "test-web" not in ollama_servers


# ==================== Unified Client Tests ====================

class TestUnifiedMCPClient:
    """Test unified MCP client functionality"""

    def test_client_initialization(self, sample_config):
        """Test client initializes correctly"""
        client = UnifiedMCPClient(sample_config)
        assert client.config == sample_config
        assert client._executor is not None

    def test_client_list_servers(self, mock_unified_client):
        """Test listing all servers"""
        servers = mock_unified_client.list_servers()
        assert "test-ollama" in servers
        assert "test-web" in servers
        assert "test-disabled" in servers

    def test_client_list_enabled_servers(self, mock_unified_client):
        """Test listing only enabled servers"""
        servers = mock_unified_client.list_enabled_servers()
        assert "test-ollama" in servers
        assert "test-web" in servers
        assert "test-disabled" not in servers

    def test_client_get_server_info(self, mock_unified_client):
        """Test getting server information"""
        info = mock_unified_client.get_server_info("test-ollama")
        assert info is not None
        assert info.type == ServerType.OLLAMA
        assert info.enabled is True

    def test_auto_select_server(self, mock_unified_client):
        """Test automatic server selection"""
        # Query with "current" or "events" keywords should select web search
        query = "What are the current events about AI?"
        server = mock_unified_client._auto_select_server(query)
        assert server == "test-web"

        # Query with "general" or "knowledge" keywords should select ollama
        query = "What is general knowledge about quantum computing?"
        server = mock_unified_client._auto_select_server(query)
        assert server == "test-ollama"

    def test_auto_select_servers_multiple(self, mock_unified_client):
        """Test selecting multiple servers"""
        query = "What are the latest news about AI?"
        servers = mock_unified_client._auto_select_servers(query)
        assert isinstance(servers, list)
        assert len(servers) > 0
        assert "test-web" in servers

    def test_get_routing_hints(self, mock_unified_client):
        """Test getting routing hints"""
        hints = mock_unified_client.get_routing_hints()

        assert "available_servers" in hints
        assert "routing_rules" in hints
        assert "strategies" in hints
        assert "default_strategy" in hints

        # Check strategies
        assert "auto" in hints["strategies"]
        assert "manual" in hints["strategies"]
        assert "multi" in hints["strategies"]

        # Check available servers only includes enabled ones
        available_names = [s["name"] for s in hints["available_servers"]]
        assert "test-ollama" in available_names
        assert "test-web" in available_names

    @pytest.mark.asyncio
    async def test_search_disabled_server_error(self, mock_unified_client):
        """Test searching with disabled server returns error"""
        result = await mock_unified_client._search_single("test query", "test-disabled")
        assert result.startswith("Error:")
        assert "disabled" in result.lower()

    @pytest.mark.asyncio
    async def test_search_nonexistent_server_error(self, mock_unified_client):
        """Test searching with non-existent server returns error"""
        result = await mock_unified_client._search_single("test query", "nonexistent")
        assert result.startswith("Error:")
        assert "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_search_multiple_servers(self, mock_unified_client):
        """Test searching with multiple servers"""
        with patch.object(mock_unified_client, '_search_single', new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = ["Result from server 1", "Result from server 2"]

            result = await mock_unified_client._search_multiple("test query", ["test-ollama", "test-web"])

            assert isinstance(result, dict)
            assert "test-ollama" in result
            assert "test-web" in result
            assert mock_search.call_count == 2

    @pytest.mark.asyncio
    async def test_context_manager(self, sample_config):
        """Test async context manager"""
        async with UnifiedMCPClient(sample_config) as client:
            assert client is not None
            servers = client.list_servers()
            assert len(servers) > 0


# ==================== Handler Tests ====================

class TestServerHandlers:
    """Test individual server type handlers"""

    @pytest.mark.asyncio
    async def test_handle_web_search(self, mock_unified_client):
        """Test web search handler"""
        server_config = mock_unified_client.config.servers["test-web"]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Abstract": "Test abstract",
            "RelatedTopics": [{"Text": "Related 1"}, {"Text": "Related 2"}]
        }

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await mock_unified_client._handle_web_search("test query", server_config)

            assert "Test abstract" in result
            assert not result.startswith("Error:")

    @pytest.mark.asyncio
    async def test_handle_ollama(self, mock_unified_client):
        """Test Ollama handler"""
        server_config = mock_unified_client.config.servers["test-ollama"]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Test response from Ollama"}

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.return_value = mock_response
            mock_response.raise_for_status = Mock()
            mock_client_class.return_value = mock_client

            result = await mock_unified_client._handle_ollama("test query", server_config)

            assert "Test response from Ollama" in result
            assert not result.startswith("Error:")

    @pytest.mark.asyncio
    async def test_handler_timeout_error(self, mock_unified_client):
        """Test handler timeout error handling"""
        server_config = mock_unified_client.config.servers["test-ollama"]

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.side_effect = httpx.TimeoutException("Timeout")
            mock_client_class.return_value = mock_client

            result = await mock_unified_client._handle_ollama("test query", server_config)

            assert result.startswith("Error:")
            assert "Timeout" in result or "timeout" in result.lower()

    @pytest.mark.asyncio
    async def test_handler_http_error(self, mock_unified_client):
        """Test handler HTTP error handling"""
        server_config = mock_unified_client.config.servers["test-ollama"]

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post.side_effect = httpx.HTTPError("Connection failed")
            mock_client_class.return_value = mock_client

            result = await mock_unified_client._handle_ollama("test query", server_config)

            assert result.startswith("Error:")


# ==================== Integration Tests ====================

class TestIntegration:
    """Integration tests for complete workflows"""

    @pytest.mark.asyncio
    async def test_auto_routing_workflow(self, mock_unified_client):
        """Test complete auto routing workflow"""
        with patch.object(mock_unified_client, '_search_single', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = "Test result"

            result = await mock_unified_client.search(
                query="What are the latest AI developments?",
                strategy=RoutingStrategy.AUTO
            )

            assert result == "Test result"
            assert mock_search.called

    @pytest.mark.asyncio
    async def test_manual_routing_workflow(self, mock_unified_client):
        """Test complete manual routing workflow"""
        with patch.object(mock_unified_client, '_search_single', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = "Test result"

            result = await mock_unified_client.search(
                query="test query",
                servers=["test-ollama"],
                strategy=RoutingStrategy.MANUAL
            )

            assert result == "Test result"
            mock_search.assert_called_once()

    @pytest.mark.asyncio
    async def test_multi_routing_workflow(self, mock_unified_client):
        """Test complete multi-server routing workflow"""
        with patch.object(mock_unified_client, '_search_single', new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = ["Result 1", "Result 2"]

            result = await mock_unified_client.search(
                query="What are the latest AI developments?",
                strategy=RoutingStrategy.MULTI
            )

            assert isinstance(result, dict)
            assert len(result) > 0
            assert mock_search.call_count >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
