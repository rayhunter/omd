"""
Test script for MCP SDK integration
Tests the new MCP client wrapper and web-search functionality
"""

import asyncio
import sys
from pathlib import Path

# Add enhanced_agent to path
sys.path.insert(0, str(Path(__file__).parent / "enhanced_agent" / "src"))

from mcp_client_wrapper import MCPClientWrapper
from loguru import logger


async def test_mcp_web_search():
    """Test MCP web-search server"""
    logger.info("🧪 Testing MCP web-search integration...")
    
    client = MCPClientWrapper()
    
    try:
        # List available MCP servers
        servers = client.get_available_servers()
        logger.info(f"📋 Available MCP servers: {servers}")
        
        # Test if mcp-web-search is available
        if 'mcp-web-search' not in servers:
            logger.warning("⚠️  mcp-web-search not found in MCP config")
            return False
        
        # List tools available on mcp-web-search
        logger.info("🔍 Listing tools on mcp-web-search...")
        tools = await client.list_tools('mcp-web-search')
        logger.info(f"🛠️  Available tools: {[t['name'] for t in tools]}")
        
        # Test a weather query
        logger.info("🌤️  Testing weather query...")
        result = await client.call_tool(
            server_name='mcp-web-search',
            tool_name='search_web',
            arguments={'query': 'weather in Oakland California this week'}
        )
        
        if result:
            logger.success(f"✅ Got result ({len(result)} chars):")
            logger.info(result[:500])  # Print first 500 chars
            return True
        else:
            logger.error("❌ No result returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await client.close_all_sessions()


async def test_unified_mcp_client():
    """Test UnifiedMCPClient with MCP integration"""
    logger.info("🧪 Testing UnifiedMCPClient with MCP...")
    
    from unified_mcp_client import UnifiedMCPClient
    
    client = UnifiedMCPClient()
    
    try:
        # Test weather query
        logger.info("🌤️  Testing weather query through UnifiedMCPClient...")
        result = await client.search(
            query="weather in Oakland California this week",
            servers=["web-search"]
        )
        
        if result and len(result) > 50:
            logger.success(f"✅ Got result ({len(result)} chars):")
            logger.info(result[:500])
            return True
        else:
            logger.warning(f"⚠️  Got short result: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await client.close()


async def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("🚀 Starting MCP Integration Tests")
    logger.info("=" * 60)
    
    # Test 1: Direct MCP client wrapper
    test1_passed = await test_mcp_web_search()
    
    logger.info("\n" + "=" * 60)
    
    # Test 2: UnifiedMCPClient integration
    test2_passed = await test_unified_mcp_client()
    
    logger.info("\n" + "=" * 60)
    logger.info("📊 Test Results:")
    logger.info(f"  MCP Client Wrapper: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    logger.info(f"  UnifiedMCPClient:   {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    logger.info("=" * 60)
    
    return test1_passed and test2_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

