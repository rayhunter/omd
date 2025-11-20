"""
MCP Client Wrapper - Proper integration with MCP SDK
Handles communication with actual MCP servers using the MCP protocol
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from loguru import logger

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClientWrapper:
    """Wrapper for MCP SDK client to communicate with MCP servers"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize MCP client wrapper
        
        Args:
            config_path: Path to MCP configuration file (defaults to ~/.cursor/mcp.json)
        """
        if config_path is None:
            config_path = str(Path.home() / ".cursor" / "mcp.json")
        
        self.config_path = config_path
        self.config = self._load_config()
        self.active_sessions: Dict[str, tuple] = {}  # Store (session, context_managers)
        
    def _load_config(self) -> Dict[str, Any]:
        """Load MCP server configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                return config.get('mcpServers', {})
        except FileNotFoundError:
            logger.warning(f"MCP config not found at {self.config_path}")
            return {}
        except Exception as e:
            logger.error(f"Error loading MCP config: {e}")
            return {}
    
    def get_available_servers(self) -> List[str]:
        """Get list of configured MCP servers"""
        return list(self.config.keys())
    
    async def _create_session(self, server_name: str) -> Optional[tuple]:
        """
        Create a new MCP client session for a server
        
        Args:
            server_name: Name of the MCP server
            
        Returns:
            Tuple of (session, context_managers) or None if failed
        """
        if server_name not in self.config:
            logger.error(f"Server '{server_name}' not found in MCP config")
            return None
        
        server_config = self.config[server_name]
        
        try:
            # Handle URL-based servers (SSE)
            if 'url' in server_config:
                logger.warning(f"URL-based MCP servers not yet supported: {server_name}")
                return None
            
            # Handle command-based servers (stdio)
            if 'command' in server_config:
                command = server_config['command']
                args = server_config.get('args', [])
                env = server_config.get('env', {})
                
                server_params = StdioServerParameters(
                    command=command,
                    args=args,
                    env=env
                )
                
                # Create stdio client context
                stdio_transport = stdio_client(server_params)
                read, write = await stdio_transport.__aenter__()
                
                # Create session
                session = ClientSession(read, write)
                await session.__aenter__()
                
                # Initialize the session
                await session.initialize()
                
                logger.info(f"✅ Connected to MCP server: {server_name}")
                # Store both the session and the transport context manager
                return (session, stdio_transport)
            
            logger.error(f"Invalid server config for {server_name}: no 'command' or 'url'")
            return None
            
        except Exception as e:
            logger.error(f"Failed to create session for {server_name}: {e}")
            return None
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """
        Call a tool on an MCP server
        
        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool response as string or None if failed
        """
        try:
            # Create session if not exists
            if server_name not in self.active_sessions:
                session_tuple = await self._create_session(server_name)
                if session_tuple is None:
                    return None
                self.active_sessions[server_name] = session_tuple
            
            session, _ = self.active_sessions[server_name]
            
            # Call the tool
            result = await session.call_tool(tool_name, arguments)
            
            # Extract text content from result
            if hasattr(result, 'content') and result.content:
                text_parts = []
                for content_item in result.content:
                    if hasattr(content_item, 'text'):
                        text_parts.append(content_item.text)
                return '\n'.join(text_parts)
            
            return str(result)
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_name} on {server_name}: {e}")
            return None
    
    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """
        List available tools on an MCP server
        
        Args:
            server_name: Name of the MCP server
            
        Returns:
            List of tool definitions
        """
        try:
            # Create session if not exists
            if server_name not in self.active_sessions:
                session_tuple = await self._create_session(server_name)
                if session_tuple is None:
                    return []
                self.active_sessions[server_name] = session_tuple
            
            session, _ = self.active_sessions[server_name]
            
            # List tools
            tools_result = await session.list_tools()
            
            return [
                {
                    'name': tool.name,
                    'description': tool.description if hasattr(tool, 'description') else '',
                    'inputSchema': tool.inputSchema if hasattr(tool, 'inputSchema') else {}
                }
                for tool in tools_result.tools
            ]
            
        except Exception as e:
            logger.error(f"Error listing tools for {server_name}: {e}")
            return []
    
    async def close_session(self, server_name: str):
        """Close an active MCP session"""
        if server_name in self.active_sessions:
            try:
                session, transport = self.active_sessions[server_name]
                # Close in reverse order: session first, then transport
                await session.__aexit__(None, None, None)
                await transport.__aexit__(None, None, None)
                del self.active_sessions[server_name]
                logger.info(f"Closed session for {server_name}")
            except Exception as e:
                logger.error(f"Error closing session for {server_name}: {e}")
    
    async def close_all_sessions(self):
        """Close all active MCP sessions"""
        for server_name in list(self.active_sessions.keys()):
            await self.close_session(server_name)


# Convenience function for simple queries
async def query_mcp_server(server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
    """
    Simple function to query an MCP server
    
    Args:
        server_name: Name of the MCP server (e.g., 'mcp-web-search')
        tool_name: Name of the tool to call (e.g., 'search_web')
        arguments: Tool arguments
        
    Returns:
        Tool response as string or None if failed
    """
    client = MCPClientWrapper()
    try:
        result = await client.call_tool(server_name, tool_name, arguments)
        return result
    finally:
        await client.close_all_sessions()

