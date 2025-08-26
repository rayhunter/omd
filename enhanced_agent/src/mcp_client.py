import json
import requests
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

class MCPClient:
    def __init__(self, config_file: str = "../config/mcp.json"):
        """Initialize MCP client with configuration file."""
        self.config = self._load_config(config_file)
        self.default_server = self.config.get("default_server", "llama-mcp")
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load MCP configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: MCP config file {config_file} not found. Using default configuration.")
            return {
                "servers": {
                    "llama-mcp": {
                        "url": "http://localhost:11434",
                        "model": "llama2",
                        "context_length": 4096,
                        "temperature": 0.7,
                        "max_tokens": 2048
                    }
                },
                "default_server": "llama-mcp"
            }
    
    def search(self, query: str, server: Optional[str] = None) -> str:
        """Search using the specified MCP server."""
        server_name = server or self.default_server
        server_config = self.config["servers"].get(server_name)
        
        if not server_config:
            raise ValueError(f"Server '{server_name}' not found in configuration")
        
        if server_name == "llama-mcp":
            return self._llama_search(query, server_config)
        elif server_name == "playwright":
            return self._playwright_search(query, server_config)
        else:
            raise ValueError(f"Unsupported server type: {server_name}")
    
    def _llama_search(self, query: str, config: Dict[str, Any]) -> str:
        """Search using Ollama/Llama MCP server."""
        try:
            url = f"{config['url']}/api/generate"
            payload = {
                "model": config.get("model", "llama2"),
                "prompt": f"Please provide information about: {query}",
                "stream": False,
                "options": {
                    "temperature": config.get("temperature", 0.7),
                    "num_predict": config.get("max_tokens", 2048)
                }
            }
            
            response = requests.post(url, json=payload, timeout=config.get("timeout", 60))
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "No response from Llama MCP server")
            
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Llama MCP server: {e}")
            return f"Error: Could not connect to Llama MCP server. Please ensure Ollama is running."
    
    def _playwright_search(self, query: str, config: Dict[str, Any]) -> str:
        """Search using Playwright MCP server."""
        try:
            url = f"{config['url']}/search"
            payload = {"query": query}
            
            response = requests.post(url, json=payload, timeout=config.get("timeout", 30000))
            response.raise_for_status()
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Playwright MCP server: {e}")
            return f"Error: Could not connect to Playwright MCP server."
    
    def list_servers(self) -> list:
        """List available MCP servers."""
        return list(self.config["servers"].keys())
    
    def get_server_info(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific server."""
        return self.config["servers"].get(server_name) 