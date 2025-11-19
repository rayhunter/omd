"""
Unified MCP Configuration Schema and Validation Utilities

This module provides a centralized configuration management system for MCP clients,
supporting environment variable substitution, validation, and schema normalization.
"""

import json
import os
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class ServerType(str, Enum):
    """Supported MCP server types"""
    OLLAMA = "ollama"
    WEB_SEARCH = "web_search"
    WIKIPEDIA = "wikipedia"
    WIKIDATA = "wikidata"
    DBPEDIA = "dbpedia"
    ARXIV = "arxiv"
    NEWS = "news"
    GITHUB = "github"
    FINANCE = "finance"
    WEATHER = "weather"
    PLAYWRIGHT = "playwright"


class RoutingStrategy(str, Enum):
    """Server selection strategies"""
    AUTO = "auto"  # Automatically select servers based on query analysis
    MANUAL = "manual"  # User explicitly specifies servers
    MULTI = "multi"  # Query multiple servers and combine results


@dataclass
class ServerConfig:
    """Configuration for a single MCP server"""
    name: str
    type: ServerType
    url: str
    enabled: bool = True
    timeout: int = 30
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    context_length: Optional[int] = None
    max_results: Optional[int] = None
    capabilities: List[str] = field(default_factory=list)
    description: str = ""

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "ServerConfig":
        """Create ServerConfig from dictionary"""
        # Extract known fields
        server_type = ServerType(data.get("type", name))

        return cls(
            name=name,
            type=server_type,
            url=data["url"],
            enabled=data.get("enabled", True),
            timeout=data.get("timeout", 30),
            max_tokens=data.get("max_tokens"),
            temperature=data.get("temperature"),
            api_key=data.get("api_key"),
            model=data.get("model"),
            context_length=data.get("context_length"),
            max_results=data.get("max_results"),
            capabilities=data.get("capabilities", []),
            description=data.get("description", ""),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            "name": self.name,
            "type": self.type.value,
            "url": self.url,
            "enabled": self.enabled,
            "timeout": self.timeout,
        }

        # Add optional fields if present
        if self.max_tokens is not None:
            result["max_tokens"] = self.max_tokens
        if self.temperature is not None:
            result["temperature"] = self.temperature
        if self.api_key is not None:
            result["api_key"] = self.api_key
        if self.model is not None:
            result["model"] = self.model
        if self.context_length is not None:
            result["context_length"] = self.context_length
        if self.max_results is not None:
            result["max_results"] = self.max_results
        if self.capabilities:
            result["capabilities"] = self.capabilities
        if self.description:
            result["description"] = self.description

        return result


@dataclass
class MCPConfig:
    """Unified MCP configuration"""
    servers: Dict[str, ServerConfig]
    default_server: str
    server_selection_strategy: RoutingStrategy = RoutingStrategy.AUTO
    fallback_servers: List[str] = field(default_factory=list)
    routing_rules: Dict[str, List[str]] = field(default_factory=dict)

    def get_enabled_servers(self) -> List[str]:
        """Get list of enabled server names"""
        return [name for name, config in self.servers.items() if config.enabled]

    def get_servers_by_capability(self, capability: str) -> List[str]:
        """Get servers that have a specific capability"""
        return [
            name for name, config in self.servers.items()
            if config.enabled and capability in config.capabilities
        ]

    def get_servers_by_type(self, server_type: ServerType) -> List[str]:
        """Get servers of a specific type"""
        return [
            name for name, config in self.servers.items()
            if config.enabled and config.type == server_type
        ]


class MCPConfigLoader:
    """Loads and validates MCP configuration with environment variable substitution"""

    DEFAULT_CONFIG_PATHS = [
        "enhanced_agent/config/mcp_extended.json",
        "enhanced_agent/config/mcp.json",
        "config/mcp.json",
        "mcp.json"
    ]

    @staticmethod
    def _replace_env_vars(content: str) -> str:
        """
        Replace environment variables in format ${VAR_NAME} with their values.
        If the environment variable is not set, keeps the placeholder.
        """
        def replacer(match):
            var_name = match.group(1)
            value = os.getenv(var_name)
            if value is None:
                # Keep placeholder if not found (allows detection of missing vars)
                return f"${{{var_name}}}"
            return value

        return re.sub(r'\$\{([^}]+)\}', replacer, content)

    @staticmethod
    def _validate_server_config(name: str, config: Dict[str, Any]) -> List[str]:
        """
        Validate a single server configuration.
        Returns list of validation errors (empty if valid).
        """
        errors = []

        # Check required fields
        if "url" not in config:
            errors.append(f"Server '{name}': missing required field 'url'")

        # Check server type
        server_type = config.get("type", name)
        try:
            ServerType(server_type)
        except ValueError:
            valid_types = [t.value for t in ServerType]
            errors.append(
                f"Server '{name}': invalid type '{server_type}'. "
                f"Valid types: {', '.join(valid_types)}"
            )

        # Check for API keys that are not configured
        if "api_key" in config:
            api_key = config["api_key"]
            if api_key and api_key.startswith("${") and api_key.endswith("}"):
                var_name = api_key[2:-1]
                errors.append(
                    f"Server '{name}': API key environment variable '{var_name}' is not set. "
                    f"This server may not work correctly."
                )

        # Validate numeric fields
        for field, field_type in [
            ("timeout", int), ("max_tokens", int), ("temperature", float),
            ("context_length", int), ("max_results", int)
        ]:
            if field in config:
                value = config[field]
                if not isinstance(value, (int, float)):
                    errors.append(f"Server '{name}': '{field}' must be a number")
                elif field == "temperature" and not (0 <= value <= 2):
                    errors.append(f"Server '{name}': temperature should be between 0 and 2")
                elif field in ["timeout", "max_tokens", "context_length", "max_results"] and value < 0:
                    errors.append(f"Server '{name}': '{field}' must be non-negative")

        return errors

    @classmethod
    def load_from_file(cls, config_path: Optional[str] = None) -> MCPConfig:
        """
        Load and validate MCP configuration from a JSON file.

        Args:
            config_path: Path to config file. If None, searches default locations.

        Returns:
            Validated MCPConfig instance

        Raises:
            FileNotFoundError: If config file not found
            ValueError: If config is invalid
        """
        # Find config file
        if config_path is None:
            config_path = cls._find_config_file()

        if not config_path or not Path(config_path).exists():
            raise FileNotFoundError(
                f"MCP config file not found. Searched: {', '.join(cls.DEFAULT_CONFIG_PATHS)}"
            )

        # Load and parse JSON with environment variable substitution
        with open(config_path, 'r') as f:
            content = f.read()
            content = cls._replace_env_vars(content)
            raw_config = json.loads(content)

        # Validate and parse
        return cls._parse_config(raw_config)

    @classmethod
    def _find_config_file(cls) -> Optional[str]:
        """Search for config file in default locations"""
        for path in cls.DEFAULT_CONFIG_PATHS:
            full_path = Path(path)
            if full_path.exists():
                return str(full_path)
        return None

    @classmethod
    def _parse_config(cls, raw_config: Dict[str, Any]) -> MCPConfig:
        """
        Parse and validate raw configuration dictionary.

        Raises:
            ValueError: If configuration is invalid
        """
        errors = []

        # Check required top-level fields
        if "servers" not in raw_config:
            errors.append("Missing required field 'servers'")
            raise ValueError("Invalid MCP configuration:\n" + "\n".join(errors))

        # Validate and parse servers
        servers = {}
        for name, server_data in raw_config["servers"].items():
            # Validate server config
            server_errors = cls._validate_server_config(name, server_data)
            errors.extend(server_errors)

            # Parse server config (even if there are warnings)
            try:
                servers[name] = ServerConfig.from_dict(name, server_data)
            except Exception as e:
                errors.append(f"Server '{name}': failed to parse config: {str(e)}")

        # Get default server
        default_server = raw_config.get("default_server", "llama-mcp")
        if default_server not in servers:
            errors.append(
                f"default_server '{default_server}' not found in servers list. "
                f"Available servers: {', '.join(servers.keys())}"
            )

        # Validate strategy
        strategy_str = raw_config.get("server_selection_strategy", "auto")
        try:
            strategy = RoutingStrategy(strategy_str)
        except ValueError:
            valid_strategies = [s.value for s in RoutingStrategy]
            errors.append(
                f"Invalid server_selection_strategy '{strategy_str}'. "
                f"Valid values: {', '.join(valid_strategies)}"
            )
            strategy = RoutingStrategy.AUTO

        # Validate fallback servers
        fallback_servers = raw_config.get("fallback_servers", [])
        for server_name in fallback_servers:
            if server_name not in servers:
                errors.append(f"Fallback server '{server_name}' not found in servers list")

        # Validate routing rules
        routing_rules = raw_config.get("routing_rules", {})
        for topic, server_list in routing_rules.items():
            for server_name in server_list:
                if server_name not in servers:
                    errors.append(
                        f"Routing rule '{topic}': server '{server_name}' not found in servers list"
                    )

        # Report errors if any critical ones exist
        critical_errors = [e for e in errors if not e.endswith("may not work correctly.")]
        if critical_errors:
            raise ValueError("Invalid MCP configuration:\n" + "\n".join(critical_errors))

        # Log warnings for non-critical errors
        warnings = [e for e in errors if e.endswith("may not work correctly.")]
        if warnings:
            print("⚠️  MCP Configuration Warnings:")
            for warning in warnings:
                print(f"  - {warning}")

        return MCPConfig(
            servers=servers,
            default_server=default_server,
            server_selection_strategy=strategy,
            fallback_servers=fallback_servers,
            routing_rules=routing_rules
        )

    @staticmethod
    def save_to_file(config: MCPConfig, config_path: str):
        """Save configuration to JSON file"""
        data = {
            "servers": {
                name: server.to_dict()
                for name, server in config.servers.items()
            },
            "default_server": config.default_server,
            "server_selection_strategy": config.server_selection_strategy.value,
            "fallback_servers": config.fallback_servers,
            "routing_rules": config.routing_rules
        }

        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)


# Convenience function for quick config loading
def load_mcp_config(config_path: Optional[str] = None) -> MCPConfig:
    """
    Load MCP configuration from file.

    Args:
        config_path: Optional path to config file. If None, searches default locations.

    Returns:
        Validated MCPConfig instance
    """
    return MCPConfigLoader.load_from_file(config_path)
