import json
import requests
import asyncio
import os
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET

class EnhancedMCPClient:
    def __init__(self, config_file: str = None):
        """Initialize Enhanced MCP client with configuration file."""
        if config_file is None:
            # Use absolute path to config file
            config_file = Path(__file__).parent.parent / "config" / "mcp.json"
        self.config = self._load_config(config_file)
        self.default_server = self.config.get("default_server", "llama-mcp")
        self.routing_rules = self.config.get("routing_rules", {})
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load MCP configuration from JSON file."""
        try:
            config_path = Path(config_file)
            with open(config_path, 'r') as f:
                content = f.read()
                # Replace environment variables
                content = self._replace_env_vars(content)
                return json.loads(content)
        except FileNotFoundError:
            print(f"Warning: MCP config file {config_file} not found. Using basic configuration.")
            return {
                "servers": {
                    "llama-mcp": {
                        "type": "ollama",
                        "url": "http://localhost:11434",
                        "model": "gemma2:2b",
                        "context_length": 4096,
                        "temperature": 0.7,
                        "max_tokens": 1024,
                        "timeout": 60
                    }
                },
                "default_server": "llama-mcp",
                "routing_rules": {}
            }
    
    def _replace_env_vars(self, content: str) -> str:
        """Replace environment variables in config content."""
        def replacer(match):
            var_name = match.group(1)
            return os.getenv(var_name, f"${{{var_name}}}")  # Keep placeholder if not found
        
        return re.sub(r'\$\{([^}]+)\}', replacer, content)
    
    def auto_select_servers(self, query: str) -> List[str]:
        """Automatically select appropriate servers based on query content."""
        query_lower = query.lower()
        selected_servers = []
        
        # Check routing rules
        for topic, servers in self.routing_rules.items():
            if any(keyword in query_lower for keyword in topic.split('_')):
                selected_servers.extend(servers)
        
        # If no specific rules matched, use fallback
        if not selected_servers:
            selected_servers = self.config.get("fallback_servers", [self.default_server])
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(selected_servers))
    
    def search(self, query: str, servers: Optional[List[str]] = None) -> Dict[str, str]:
        """Search using specified servers or auto-select based on query."""
        if servers is None:
            servers = self.auto_select_servers(query)
        
        results = {}
        for server_name in servers:
            try:
                result = self.search_single_server(query, server_name)
                if result and not result.startswith("Error:"):
                    results[server_name] = result
            except Exception as e:
                results[server_name] = f"Error: {str(e)}"
        
        return results
    
    def search_single_server(self, query: str, server: str) -> str:
        """Search using a single specified MCP server."""
        server_config = self.config["servers"].get(server)
        
        if not server_config:
            raise ValueError(f"Server '{server}' not found in configuration")
        
        server_type = server_config.get("type", server)
        
        # Route to appropriate handler based on server type
        handlers = {
            "ollama": self._ollama_search,
            "web_search": self._web_search,
            "wikipedia": self._wikipedia_search,
            "wikidata": self._wikidata_search,
            "dbpedia": self._dbpedia_search,
            "arxiv": self._arxiv_search,
            "news": self._news_search,
            "github": self._github_search,
            "finance": self._finance_search,
            "weather": self._weather_search,
            "playwright": self._playwright_search
        }
        
        handler = handlers.get(server_type)
        if not handler:
            raise ValueError(f"Unsupported server type: {server_type}")
        
        return handler(query, server_config)
    
    def _ollama_search(self, query: str, config: Dict[str, Any]) -> str:
        """Search using Ollama/Llama MCP server."""
        try:
            url = f"{config['url']}/api/generate"
            payload = {
                "model": config.get("model", "llama2"),
                "prompt": f"Please provide comprehensive information about: {query}",
                "stream": False,
                "options": {
                    "temperature": config.get("temperature", 0.7),
                    "num_predict": config.get("max_tokens", 1024)
                }
            }
            
            response = requests.post(url, json=payload, timeout=config.get("timeout", 60))
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "No response from Ollama server")
            
        except requests.exceptions.RequestException as e:
            return f"Error: Could not connect to Ollama server. Please ensure Ollama is running. ({str(e)})"
    
    def _web_search(self, query: str, config: Dict[str, Any]) -> str:
        """Search using DuckDuckGo Instant Answer API."""
        try:
            # Use DuckDuckGo Instant Answer API (no API key required)
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = requests.get(url, params=params, timeout=config.get("timeout", 30))
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant information
            results = []
            if data.get("Abstract"):
                results.append(f"Summary: {data['Abstract']}")
            
            if data.get("RelatedTopics"):
                related = [topic.get("Text", "") for topic in data["RelatedTopics"][:3]]
                if related:
                    results.append(f"Related: {'; '.join(related)}")
            
            return "\n".join(results) if results else "No specific instant answer found."
            
        except requests.exceptions.RequestException as e:
            return f"Error: Could not perform web search. ({str(e)})"
    
    def _wikipedia_search(self, query: str, config: Dict[str, Any]) -> str:
        """Search using Wikipedia API."""
        try:
            # First, search for the page
            search_url = f"{config['url']}/page/summary/{quote_plus(query)}"
            response = requests.get(search_url, timeout=config.get("timeout", 30))
            
            if response.status_code == 200:
                data = response.json()
                extract = data.get("extract", "")
                if extract:
                    return f"Wikipedia: {extract}"
            
            # If direct lookup fails, try search
            search_url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": query,
                "srlimit": 1
            }
            
            response = requests.get(search_url, params=params, timeout=config.get("timeout", 30))
            response.raise_for_status()
            
            data = response.json()
            if data["query"]["search"]:
                title = data["query"]["search"][0]["title"]
                snippet = data["query"]["search"][0]["snippet"]
                # Remove HTML tags
                snippet = re.sub(r'<[^>]+>', '', snippet)
                return f"Wikipedia ({title}): {snippet}"
            
            return "No Wikipedia articles found for this query."

        except requests.exceptions.RequestException as e:
            return f"Error: Could not search Wikipedia. ({str(e)})"

    def _wikidata_search(self, query: str, config: Dict[str, Any]) -> str:
        """Search using Wikidata SPARQL endpoint."""
        try:
            url = config["url"]

            # Simple SPARQL query to search for entities
            sparql_query = f"""
            SELECT ?item ?itemLabel ?description WHERE {{
              ?item ?label "{query}"@en.
              ?item schema:description ?description.
              FILTER(LANG(?description) = "en")
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
            }}
            LIMIT 5
            """

            params = {
                "query": sparql_query,
                "format": "json"
            }

            response = requests.get(url, params=params, timeout=config.get("timeout", 30))
            response.raise_for_status()

            data = response.json()
            results = data.get("results", {}).get("bindings", [])

            if results:
                formatted_results = []
                for result in results[:3]:
                    label = result.get("itemLabel", {}).get("value", "Unknown")
                    description = result.get("description", {}).get("value", "No description")
                    formatted_results.append(f"🔍 {label}: {description}")
                return "\n".join(formatted_results)

            return "No Wikidata entities found for this query."

        except requests.exceptions.RequestException as e:
            return f"Error: Could not search Wikidata. ({str(e)})"

    def _dbpedia_search(self, query: str, config: Dict[str, Any]) -> str:
        """Search using DBpedia SPARQL endpoint."""
        try:
            url = config["url"]

            # Simple SPARQL query to search DBpedia
            sparql_query = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dbo: <http://dbpedia.org/ontology/>

            SELECT ?subject ?label ?abstract WHERE {{
              ?subject rdfs:label ?label.
              ?subject dbo:abstract ?abstract.
              FILTER(LANG(?label) = "en" && LANG(?abstract) = "en")
              FILTER(regex(?label, "{query}", "i"))
            }}
            LIMIT 3
            """

            params = {
                "query": sparql_query,
                "format": "json"
            }

            response = requests.get(url, params=params, timeout=config.get("timeout", 30))
            response.raise_for_status()

            data = response.json()
            results = data.get("results", {}).get("bindings", [])

            if results:
                formatted_results = []
                for result in results:
                    label = result.get("label", {}).get("value", "Unknown")
                    abstract = result.get("abstract", {}).get("value", "No description")
                    # Truncate abstract
                    abstract = abstract[:200] + "..." if len(abstract) > 200 else abstract
                    formatted_results.append(f"📚 {label}: {abstract}")
                return "\n".join(formatted_results)

            return "No DBpedia resources found for this query."

        except requests.exceptions.RequestException as e:
            return f"Error: Could not search DBpedia. ({str(e)})"

    def _arxiv_search(self, query: str, config: Dict[str, Any]) -> str:
        """Search using arXiv API."""
        try:
            url = config["url"]
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": config.get("max_results", 5),
                "sortBy": "relevance",
                "sortOrder": "descending"
            }
            
            response = requests.get(url, params=params, timeout=config.get("timeout", 30))
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            results = []
            for entry in entries[:3]:  # Limit to top 3 results
                title = entry.find('.//{http://www.w3.org/2005/Atom}title').text
                summary = entry.find('.//{http://www.w3.org/2005/Atom}summary').text
                # Truncate summary
                summary = summary[:200] + "..." if len(summary) > 200 else summary
                results.append(f"📄 {title}: {summary}")
            
            return "\n".join(results) if results else "No arXiv papers found for this query."
            
        except (requests.exceptions.RequestException, ET.ParseError) as e:
            return f"Error: Could not search arXiv. ({str(e)})"
    
    def _news_search(self, query: str, config: Dict[str, Any]) -> str:
        """Search using News API (requires API key)."""
        api_key = config.get("api_key")
        if not api_key or api_key.startswith("${"):
            return "Error: News API key not configured. Set NEWS_API_KEY environment variable."
        
        try:
            url = f"{config['url']}/everything"
            params = {
                "q": query,
                "apiKey": api_key,
                "pageSize": config.get("max_results", 5),
                "sortBy": "publishedAt"
            }
            
            response = requests.get(url, params=params, timeout=config.get("timeout", 30))
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
            
        except requests.exceptions.RequestException as e:
            return f"Error: Could not search news. ({str(e)})"
    
    def _github_search(self, query: str, config: Dict[str, Any]) -> str:
        """Search using GitHub API."""
        try:
            url = f"{config['url']}/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": config.get("max_results", 5)
            }
            
            headers = {}
            api_key = config.get("api_key")
            if api_key and not api_key.startswith("${"):
                headers["Authorization"] = f"token {api_key}"
            
            response = requests.get(url, params=params, headers=headers, timeout=config.get("timeout", 30))
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
            
        except requests.exceptions.RequestException as e:
            return f"Error: Could not search GitHub. ({str(e)})"
    
    def _finance_search(self, query: str, config: Dict[str, Any]) -> str:
        """Search using Yahoo Finance API."""
        try:
            # Simple stock symbol lookup
            symbol = query.upper().replace(" ", "")
            url = f"{config['url']}/{symbol}"
            params = {
                "interval": "1d",
                "range": "1d"
            }
            
            response = requests.get(url, params=params, timeout=config.get("timeout", 30))
            response.raise_for_status()
            
            data = response.json()
            chart = data.get("chart", {})
            
            if chart.get("result"):
                result = chart["result"][0]
                meta = result.get("meta", {})
                current_price = meta.get("regularMarketPrice", "N/A")
                prev_close = meta.get("previousClose", "N/A")
                
                if current_price != "N/A" and prev_close != "N/A":
                    change = current_price - prev_close
                    change_pct = (change / prev_close) * 100
                    return f"💹 {symbol}: ${current_price:.2f} ({change:+.2f}, {change_pct:+.2f}%)"
            
            return f"No financial data found for '{query}'"
            
        except requests.exceptions.RequestException as e:
            return f"Error: Could not get financial data. ({str(e)})"
    
    def _weather_search(self, query: str, config: Dict[str, Any]) -> str:
        """Search using OpenWeatherMap API."""
        api_key = config.get("api_key")
        if not api_key or api_key.startswith("${"):
            return "Error: Weather API key not configured. Set WEATHER_API_KEY environment variable."
        
        try:
            url = f"{config['url']}/weather"
            params = {
                "q": query,
                "appid": api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=config.get("timeout", 30))
            response.raise_for_status()
            
            data = response.json()
            
            city = data.get("name", "Unknown")
            country = data.get("sys", {}).get("country", "")
            temp = data.get("main", {}).get("temp", "N/A")
            description = data.get("weather", [{}])[0].get("description", "No description")
            
            return f"🌤️ {city}, {country}: {temp}°C, {description.title()}"
            
        except requests.exceptions.RequestException as e:
            return f"Error: Could not get weather data. ({str(e)})"
    
    def _playwright_search(self, query: str, config: Dict[str, Any]) -> str:
        """Search using Playwright MCP server."""
        try:
            url = f"{config['url']}/search"
            payload = {"query": query}
            
            response = requests.post(url, json=payload, timeout=config.get("timeout", 30))
            response.raise_for_status()
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            return f"Error: Could not connect to Playwright MCP server. ({str(e)})"
    
    def list_servers(self, include_disabled: bool = False) -> List[str]:
        """
        List available MCP servers.

        Args:
            include_disabled: If True, include disabled servers. Default is False.

        Returns:
            List of server names
        """
        if include_disabled:
            return list(self.config["servers"].keys())
        else:
            return [
                name for name, config in self.config["servers"].items()
                if config.get("enabled", True)  # Default to True if not specified
            ]
    
    def get_server_info(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific server."""
        return self.config["servers"].get(server_name)
    
    def get_server_capabilities(self, server_name: str) -> List[str]:
        """Get capabilities of a specific server."""
        server_info = self.get_server_info(server_name)
        return server_info.get("capabilities", []) if server_info else []
    
    def list_servers_by_capability(self, capability: str) -> List[str]:
        """List servers that have a specific capability."""
        servers = []
        for server_name, config in self.config["servers"].items():
            if capability in config.get("capabilities", []):
                servers.append(server_name)
        return servers
