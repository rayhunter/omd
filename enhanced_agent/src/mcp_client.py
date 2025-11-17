import json
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
import httpx
from concurrent.futures import ThreadPoolExecutor

class MCPClient:
    def __init__(self, config_file: str = None):
        """Initialize MCP client with configuration file."""
        if config_file is None:
            # Use absolute path to config file
            config_file = Path(__file__).parent.parent / "config" / "mcp.json"
        self.config = self._load_config(config_file)
        self.default_server = self.config.get("default_server", "llama-mcp")

        # Thread pool executor for blocking operations
        self._executor = ThreadPoolExecutor(max_workers=4)

        # HTTP client for async operations (will be initialized per request to avoid connection issues)
        self._http_client: Optional[httpx.AsyncClient] = None
        
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
    
    async def search(self, query: str, server: Optional[str] = None) -> str:
        """Search using the specified MCP server (async)."""
        server_name = server or self.default_server
        server_config = self.config["servers"].get(server_name)

        if not server_config:
            raise ValueError(f"Server '{server_name}' not found in configuration")

        if server_name == "llama-mcp":
            return await self._llama_search_async(query, server_config)
        elif server_name == "playwright":
            return await self._playwright_search_async(query, server_config)
        else:
            raise ValueError(f"Unsupported server type: {server_name}")
    
    async def _llama_search_async(self, query: str, config: Dict[str, Any]) -> str:
        """Search using Ollama/Llama MCP server (async with httpx)."""
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

            timeout = httpx.Timeout(config.get("timeout", 60.0))

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()

                result = response.json()
                return result.get("response", "No response from Llama MCP server")

        except httpx.TimeoutException as e:
            print(f"Timeout connecting to Llama MCP server: {e}")
            return f"Error: Timeout connecting to Llama MCP server."
        except httpx.HTTPError as e:
            print(f"Error connecting to Llama MCP server: {e}")
            return f"Error: Could not connect to Llama MCP server. Please ensure Ollama is running."
        except Exception as e:
            print(f"Unexpected error in Llama search: {e}")
            return f"Error: Unexpected error occurred during Llama search."
    
    async def _playwright_search_async(self, query: str, config: Dict[str, Any]) -> str:
        """Search using Playwright MCP server (async with httpx)."""
        try:
            url = f"{config['url']}/search"
            payload = {"query": query}

            # Note: config timeout might be in ms for playwright, convert to seconds
            timeout_value = config.get("timeout", 30)
            if timeout_value > 1000:  # Likely in milliseconds
                timeout_value = timeout_value / 1000.0
            timeout = httpx.Timeout(timeout_value)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()

                return response.text

        except httpx.TimeoutException as e:
            print(f"Timeout connecting to Playwright MCP server: {e}")
            return f"Error: Timeout connecting to Playwright MCP server."
        except httpx.HTTPError as e:
            print(f"Error connecting to Playwright MCP server: {e}")
            return f"Error: Could not connect to Playwright MCP server."
        except Exception as e:
            print(f"Unexpected error in Playwright search: {e}")
            return f"Error: Unexpected error occurred during Playwright search."
    
    def list_servers(self) -> list:
        """List available MCP servers."""
        return list(self.config["servers"].keys())

    def get_server_info(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific server."""
        return self.config["servers"].get(server_name)

    async def _run_blocking_operation(self, func, *args, **kwargs):
        """
        Run a blocking operation (e.g., blocking SDK call) in a thread pool executor.

        This is useful for libraries that don't have async support (e.g., some Ollama SDKs).

        Args:
            func: The blocking function to run
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            The result of the function call
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._executor, lambda: func(*args, **kwargs))

    async def close(self):
        """Close the MCP client and cleanup resources."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

        # Shutdown the thread pool executor
        self._executor.shutdown(wait=True)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close() 