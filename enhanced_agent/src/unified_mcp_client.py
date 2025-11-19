"""
Unified MCP Client with Routing Logic

This module provides a single, unified MCP client that combines the best features
from both the basic and enhanced clients:
- Full async/await support for non-blocking operations
- Multiple server type support (Ollama, web search, Wikipedia, arXiv, etc.)
- Intelligent routing based on query analysis
- Environment variable substitution
- Graceful error handling and fallbacks
"""

import asyncio
import httpx
import json
import re
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

from .mcp_config import (
    MCPConfig,
    ServerConfig,
    ServerType,
    RoutingStrategy,
    load_mcp_config
)


class UnifiedMCPClient:
    """
    Unified MCP client supporting multiple server types with intelligent routing.

    Features:
    - Async operations for all server types
    - Auto/manual/multi routing modes
    - Query analysis for server selection
    - Environment variable substitution
    - Comprehensive error handling
    """

    def __init__(self, config: Optional[Union[str, MCPConfig]] = None):
        """
        Initialize unified MCP client.

        Args:
            config: Either a path to config file, an MCPConfig instance, or None
                   to search default locations
        """
        # Load configuration
        if isinstance(config, MCPConfig):
            self.config = config
        elif isinstance(config, str):
            self.config = load_mcp_config(config)
        else:
            self.config = load_mcp_config()

        # Thread pool for blocking operations
        self._executor = ThreadPoolExecutor(max_workers=4)

        # HTTP client will be created per-request to avoid connection issues
        self._http_timeout = httpx.Timeout(60.0, connect=10.0)

    # ==================== Public API ====================

    async def search(
        self,
        query: str,
        servers: Optional[List[str]] = None,
        strategy: Optional[RoutingStrategy] = None
    ) -> Union[str, Dict[str, str]]:
        """
        Search using MCP servers.

        Args:
            query: The search query
            servers: Optional list of server names to use. If None, uses routing strategy.
            strategy: Routing strategy (auto/manual/multi). If None, uses config default.

        Returns:
            - If single server or auto mode: string result
            - If multi mode: dict mapping server names to results
        """
        # Determine strategy
        if strategy is None:
            strategy = self.config.server_selection_strategy

        # Determine which servers to query
        if servers is not None:
            # Manual mode: use specified servers
            server_list = servers
        elif strategy == RoutingStrategy.AUTO:
            # Auto mode: select best server based on query
            server_list = [self._auto_select_server(query)]
        elif strategy == RoutingStrategy.MULTI:
            # Multi mode: query multiple relevant servers
            server_list = self._auto_select_servers(query)
        else:
            # Fallback to default server
            server_list = [self.config.default_server]

        # Execute searches
        if len(server_list) == 1:
            # Single server: return simple result
            return await self._search_single(query, server_list[0])
        else:
            # Multiple servers: return dict of results
            return await self._search_multiple(query, server_list)

    async def _search_single(self, query: str, server_name: str) -> str:
        """Search using a single server"""
        server_config = self.config.servers.get(server_name)

        if not server_config:
            return f"Error: Server '{server_name}' not found in configuration"

        if not server_config.enabled:
            return f"Error: Server '{server_name}' is disabled"

        # Route to appropriate handler
        handler = self._get_handler(server_config.type)
        if not handler:
            return f"Error: No handler for server type '{server_config.type}'"

        try:
            return await handler(query, server_config)
        except Exception as e:
            return f"Error: {str(e)}"

    async def _search_multiple(self, query: str, server_names: List[str]) -> Dict[str, str]:
        """Search using multiple servers concurrently"""
        tasks = []
        for server_name in server_names:
            tasks.append(self._search_single(query, server_name))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Build result dict
        result_dict = {}
        for server_name, result in zip(server_names, results):
            if isinstance(result, Exception):
                result_dict[server_name] = f"Error: {str(result)}"
            else:
                result_dict[server_name] = result

        return result_dict

    def _auto_select_server(self, query: str) -> str:
        """Select single best server for query"""
        servers = self._auto_select_servers(query)
        return servers[0] if servers else self.config.default_server

    def _auto_select_servers(self, query: str) -> List[str]:
        """
        Automatically select appropriate servers based on query content.
        Uses routing rules from configuration.
        """
        query_lower = query.lower()
        selected_servers = []

        # Check routing rules
        for topic, servers in self.config.routing_rules.items():
            # Split topic into keywords (e.g., "current_events" -> ["current", "events"])
            keywords = topic.replace('_', ' ').split()
            if any(keyword in query_lower for keyword in keywords):
                # Add servers from this rule
                for server_name in servers:
                    if server_name in self.config.servers and self.config.servers[server_name].enabled:
                        selected_servers.append(server_name)

        # If no rules matched, use fallback servers
        if not selected_servers:
            selected_servers = [
                s for s in self.config.fallback_servers
                if s in self.config.servers and self.config.servers[s].enabled
            ]

        # If still no servers, use default
        if not selected_servers:
            selected_servers = [self.config.default_server]

        # Remove duplicates while preserving order
        return list(dict.fromkeys(selected_servers))

    def get_routing_hints(self) -> Dict[str, Any]:
        """
        Expose routing configuration for UI/API integration.

        Returns:
            Dict containing:
            - available_servers: List of enabled servers with metadata
            - routing_rules: Topic-based routing rules
            - strategies: Available routing strategies
            - default_strategy: Current default strategy
        """
        return {
            "available_servers": [
                {
                    "name": name,
                    "type": config.type.value,
                    "description": config.description,
                    "capabilities": config.capabilities,
                    "enabled": config.enabled
                }
                for name, config in self.config.servers.items()
            ],
            "routing_rules": self.config.routing_rules,
            "strategies": [s.value for s in RoutingStrategy],
            "default_strategy": self.config.server_selection_strategy.value,
            "fallback_servers": self.config.fallback_servers
        }

    # ==================== Server Type Handlers ====================

    def _get_handler(self, server_type: ServerType):
        """Get the appropriate handler function for a server type"""
        handlers = {
            ServerType.OLLAMA: self._handle_ollama,
            ServerType.WEB_SEARCH: self._handle_web_search,
            ServerType.WIKIPEDIA: self._handle_wikipedia,
            ServerType.WIKIDATA: self._handle_wikidata,
            ServerType.DBPEDIA: self._handle_dbpedia,
            ServerType.ARXIV: self._handle_arxiv,
            ServerType.NEWS: self._handle_news,
            ServerType.GITHUB: self._handle_github,
            ServerType.FINANCE: self._handle_finance,
            ServerType.WEATHER: self._handle_weather,
            ServerType.PLAYWRIGHT: self._handle_playwright,
        }
        return handlers.get(server_type)

    async def _handle_ollama(self, query: str, config: ServerConfig) -> str:
        """Handle Ollama/LLM server requests"""
        try:
            url = f"{config.url}/api/generate"
            payload = {
                "model": config.model or "llama2",
                "prompt": f"Please provide comprehensive information about: {query}",
                "stream": False,
                "options": {}
            }

            if config.temperature is not None:
                payload["options"]["temperature"] = config.temperature
            if config.max_tokens is not None:
                payload["options"]["num_predict"] = config.max_tokens

            timeout = httpx.Timeout(config.timeout, connect=10.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()

                result = response.json()
                return result.get("response", "No response from Ollama server")

        except httpx.TimeoutException:
            return f"Error: Timeout connecting to Ollama server (timeout: {config.timeout}s)"
        except httpx.HTTPError as e:
            return f"Error: Could not connect to Ollama server. Please ensure Ollama is running. ({str(e)})"
        except Exception as e:
            return f"Error: Unexpected error in Ollama search: {str(e)}"

    async def _handle_web_search(self, query: str, config: ServerConfig) -> str:
        """Handle web search using DuckDuckGo"""
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }

            timeout = httpx.Timeout(config.timeout, connect=10.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                # Extract relevant information
                results = []
                if data.get("Abstract"):
                    results.append(f"Summary: {data['Abstract']}")

                if data.get("RelatedTopics"):
                    related = [
                        topic.get("Text", "")
                        for topic in data["RelatedTopics"][:3]
                        if isinstance(topic, dict) and "Text" in topic
                    ]
                    if related:
                        results.append(f"Related: {'; '.join(related)}")

                return "\n".join(results) if results else "No specific instant answer found."

        except Exception as e:
            return f"Error: Could not perform web search. ({str(e)})"

    async def _handle_wikipedia(self, query: str, config: ServerConfig) -> str:
        """Handle Wikipedia API requests"""
        try:
            timeout = httpx.Timeout(config.timeout, connect=10.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                # Try direct page summary first
                search_url = f"{config.url}/page/summary/{quote_plus(query)}"
                response = await client.get(search_url)

                if response.status_code == 200:
                    data = response.json()
                    extract = data.get("extract", "")
                    if extract:
                        return f"Wikipedia: {extract}"

                # Fall back to search API
                search_url = "https://en.wikipedia.org/w/api.php"
                params = {
                    "action": "query",
                    "format": "json",
                    "list": "search",
                    "srsearch": query,
                    "srlimit": 1
                }

                response = await client.get(search_url, params=params)
                response.raise_for_status()

                data = response.json()
                if data["query"]["search"]:
                    title = data["query"]["search"][0]["title"]
                    snippet = data["query"]["search"][0]["snippet"]
                    # Remove HTML tags
                    snippet = re.sub(r'<[^>]+>', '', snippet)
                    return f"Wikipedia ({title}): {snippet}"

                return "No Wikipedia articles found for this query."

        except Exception as e:
            return f"Error: Could not search Wikipedia. ({str(e)})"

    async def _handle_wikidata(self, query: str, config: ServerConfig) -> str:
        """Handle Wikidata SPARQL queries for structured knowledge"""
        try:
            timeout = httpx.Timeout(config.timeout, connect=10.0)

            # Build SPARQL query to search for entities
            sparql_query = f"""
            SELECT ?item ?itemLabel ?itemDescription WHERE {{
              SERVICE wikibase:mwapi {{
                bd:serviceParam wikibase:api "EntitySearch" .
                bd:serviceParam wikibase:endpoint "www.wikidata.org" .
                bd:serviceParam mwapi:search "{query}" .
                bd:serviceParam mwapi:language "en" .
                ?item wikibase:apiOutputItem mwapi:item .
              }}
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
            }}
            LIMIT 3
            """

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(
                    config.url,
                    params={
                        "query": sparql_query,
                        "format": "json"
                    }
                )
                response.raise_for_status()

                data = response.json()
                results = []

                for binding in data.get("results", {}).get("bindings", []):
                    label = binding.get("itemLabel", {}).get("value", "Unknown")
                    description = binding.get("itemDescription", {}).get("value", "No description")
                    item_id = binding.get("item", {}).get("value", "").split("/")[-1]

                    results.append(f"🔷 {label} ({item_id}): {description}")

                if results:
                    return "Wikidata entities:\n" + "\n".join(results)
                else:
                    return "No Wikidata entities found for this query."

        except Exception as e:
            return f"Error: Could not search Wikidata. ({str(e)})"

    async def _handle_dbpedia(self, query: str, config: ServerConfig) -> str:
        """Handle DBpedia SPARQL queries for structured Wikipedia data"""
        try:
            timeout = httpx.Timeout(config.timeout, connect=10.0)

            # Use DBpedia Lookup service first for better entity matching
            lookup_url = "https://lookup.dbpedia.org/api/search"

            async with httpx.AsyncClient(timeout=timeout) as client:
                # Try DBpedia Lookup service (simpler and more reliable)
                response = await client.get(
                    lookup_url,
                    params={
                        "query": query,
                        "maxResults": 3,
                        "format": "json"
                    }
                )
                response.raise_for_status()

                data = response.json()
                results = []

                for doc in data.get("docs", []):
                    label = doc.get("label", ["Unknown"])[0] if isinstance(doc.get("label"), list) else doc.get("label", "Unknown")
                    description = doc.get("comment", ["No description"])[0] if isinstance(doc.get("comment"), list) else doc.get("comment", "No description")

                    # Clean HTML tags from label and description
                    if isinstance(label, str):
                        label = re.sub(r'<[^>]+>', '', label)
                    if isinstance(description, str):
                        description = re.sub(r'<[^>]+>', '', description)
                        # Truncate long descriptions
                        description = description[:300] + "..." if len(description) > 300 else description

                    results.append(f"📘 {label}: {description}")

                if results:
                    return "DBpedia results:\n" + "\n".join(results)
                else:
                    return "No DBpedia resources found for this query."

        except Exception as e:
            return f"Error: Could not search DBpedia. ({str(e)})"

    async def _handle_arxiv(self, query: str, config: ServerConfig) -> str:
        """Handle arXiv API requests"""
        try:
            url = config.url
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": config.max_results or 5,
                "sortBy": "relevance",
                "sortOrder": "descending"
            }

            timeout = httpx.Timeout(config.timeout, connect=10.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()

                # Parse XML response
                root = ET.fromstring(response.content)
                entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')

                results = []
                for entry in entries[:3]:
                    title_elem = entry.find('.//{http://www.w3.org/2005/Atom}title')
                    summary_elem = entry.find('.//{http://www.w3.org/2005/Atom}summary')

                    if title_elem is not None and summary_elem is not None:
                        title = title_elem.text
                        summary = summary_elem.text
                        summary = summary[:200] + "..." if len(summary) > 200 else summary
                        results.append(f"📄 {title}: {summary}")

                return "\n".join(results) if results else "No arXiv papers found for this query."

        except Exception as e:
            return f"Error: Could not search arXiv. ({str(e)})"

    async def _handle_news(self, query: str, config: ServerConfig) -> str:
        """Handle news API requests (requires API key)"""
        if not config.api_key or config.api_key.startswith("${"):
            return "Error: News API key not configured. Set NEWS_API_KEY environment variable."

        try:
            url = f"{config.url}/everything"
            params = {
                "q": query,
                "apiKey": config.api_key,
                "pageSize": config.max_results or 5,
                "sortBy": "publishedAt"
            }

            timeout = httpx.Timeout(config.timeout, connect=10.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()
                articles = data.get("articles", [])

                results = []
                for article in articles[:3]:
                    title = article.get("title", "")
                    description = article.get("description", "")
                    source = article.get("source", {}).get("name", "Unknown")
                    results.append(f"📰 {source}: {title} - {description}")

                return "\n".join(results) if results else "No recent news found for this query."

        except Exception as e:
            return f"Error: Could not search news. ({str(e)})"

    async def _handle_github(self, query: str, config: ServerConfig) -> str:
        """Handle GitHub API requests"""
        try:
            url = f"{config.url}/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": config.max_results or 5
            }

            headers = {}
            if config.api_key and not config.api_key.startswith("${"):
                headers["Authorization"] = f"token {config.api_key}"

            timeout = httpx.Timeout(config.timeout, connect=10.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()

                data = response.json()
                items = data.get("items", [])

                results = []
                for repo in items[:3]:
                    name = repo.get("full_name", "")
                    description = repo.get("description", "No description")
                    stars = repo.get("stargazers_count", 0)
                    results.append(f"⭐ {name} ({stars} stars): {description}")

                return "\n".join(results) if results else "No GitHub repositories found for this query."

        except Exception as e:
            return f"Error: Could not search GitHub. ({str(e)})"

    async def _handle_finance(self, query: str, config: ServerConfig) -> str:
        """Handle finance API requests (Yahoo Finance)"""
        try:
            symbol = query.upper().replace(" ", "")
            url = f"{config.url}/{symbol}"
            params = {
                "interval": "1d",
                "range": "1d"
            }

            timeout = httpx.Timeout(config.timeout, connect=10.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()
                chart = data.get("chart", {})

                if chart.get("result"):
                    result = chart["result"][0]
                    meta = result.get("meta", {})
                    current_price = meta.get("regularMarketPrice")
                    prev_close = meta.get("previousClose")

                    if current_price is not None and prev_close is not None:
                        change = current_price - prev_close
                        change_pct = (change / prev_close) * 100
                        return f"💹 {symbol}: ${current_price:.2f} ({change:+.2f}, {change_pct:+.2f}%)"

                return f"No financial data found for '{query}'"

        except Exception as e:
            return f"Error: Could not get financial data. ({str(e)})"

    async def _handle_weather(self, query: str, config: ServerConfig) -> str:
        """Handle weather API requests (OpenWeatherMap)"""
        if not config.api_key or config.api_key.startswith("${"):
            return "Error: Weather API key not configured. Set WEATHER_API_KEY environment variable."

        try:
            url = f"{config.url}/weather"
            params = {
                "q": query,
                "appid": config.api_key,
                "units": "metric"
            }

            timeout = httpx.Timeout(config.timeout, connect=10.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                city = data.get("name", "Unknown")
                country = data.get("sys", {}).get("country", "")
                temp = data.get("main", {}).get("temp", "N/A")
                description = data.get("weather", [{}])[0].get("description", "No description")

                return f"🌤️ {city}, {country}: {temp}°C, {description.title()}"

        except Exception as e:
            return f"Error: Could not get weather data. ({str(e)})"

    async def _handle_playwright(self, query: str, config: ServerConfig) -> str:
        """Handle Playwright MCP server requests"""
        try:
            url = f"{config.url}/search"
            payload = {"query": query}

            timeout = httpx.Timeout(config.timeout, connect=10.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()

                return response.text

        except Exception as e:
            return f"Error: Could not connect to Playwright MCP server. ({str(e)})"

    # ==================== Utility Methods ====================

    @property
    def default_server(self) -> str:
        """Get the default server name (backward compatibility property)"""
        return self.config.default_server

    def list_servers(self) -> List[str]:
        """List all available server names"""
        return list(self.config.servers.keys())

    def list_enabled_servers(self) -> List[str]:
        """List enabled server names"""
        return self.config.get_enabled_servers()

    def get_server_info(self, server_name: str) -> Optional[ServerConfig]:
        """Get configuration for a specific server"""
        return self.config.servers.get(server_name)

    def get_servers_by_capability(self, capability: str) -> List[str]:
        """Get servers that have a specific capability"""
        return self.config.get_servers_by_capability(capability)

    async def close(self):
        """Close the client and cleanup resources"""
        self._executor.shutdown(wait=True)

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
