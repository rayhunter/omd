"""
Test script for OpenWeatherMap MCP integration
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add enhanced_agent to path
sys.path.insert(0, str(Path(__file__).parent / "enhanced_agent" / "src"))

from mcp_client_wrapper import MCPClientWrapper
from loguru import logger


async def test_openweathermap_mcp():
    """Test OpenWeatherMap MCP server"""
    logger.info("🧪 Testing OpenWeatherMap MCP integration...")
    
    # Check if API key is set
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        logger.error("❌ OPENWEATHER_API_KEY not set in environment")
        logger.info("Please add OPENWEATHER_API_KEY to your .env file")
        return False
    
    logger.info(f"✅ API key found: {api_key[:10]}...")
    
    client = MCPClientWrapper()
    
    try:
        # List available MCP servers
        servers = client.get_available_servers()
        logger.info(f"📋 Available MCP servers: {len(servers)} servers")
        
        # Test if openweathermap is available
        if 'openweathermap' not in servers:
            logger.warning("⚠️  openweathermap not found in MCP config")
            logger.info("Available servers:", servers)
            return False
        
        logger.success("✅ openweathermap server found in config")
        
        # List tools available on openweathermap
        logger.info("🔍 Listing tools on openweathermap...")
        tools = await client.list_tools('openweathermap')
        logger.info(f"🛠️  Available tools ({len(tools)}):")
        for tool in tools:
            logger.info(f"   - {tool['name']}: {tool.get('description', 'No description')[:80]}")
        
        # Test current weather query
        logger.info("\n🌤️  Testing current weather query for Oakland, California...")
        result = await client.call_tool(
            server_name='openweathermap',
            tool_name='get-current-weather',
            arguments={'location': 'Oakland, California'}
        )
        
        if result:
            logger.success(f"✅ Got weather result ({len(result)} chars):")
            logger.info("\n" + "="*60)
            logger.info(result)
            logger.info("="*60 + "\n")
            
            # Test forecast
            logger.info("🌤️  Testing weather forecast for Oakland, California...")
            forecast = await client.call_tool(
                server_name='openweathermap',
                tool_name='get-weather-forecast',
                arguments={'location': 'Oakland, California'}
            )
            
            if forecast:
                logger.success(f"✅ Got forecast ({len(forecast)} chars):")
                logger.info("\n" + "="*60)
                logger.info(forecast[:500] + "..." if len(forecast) > 500 else forecast)
                logger.info("="*60 + "\n")
            
            return True
        else:
            logger.error("❌ No result returned from weather query")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await client.close_all_sessions()


async def test_unified_client_weather():
    """Test weather through UnifiedMCPClient"""
    logger.info("🧪 Testing weather through UnifiedMCPClient...")
    
    from unified_mcp_client import UnifiedMCPClient
    
    client = UnifiedMCPClient()
    
    try:
        # Test weather query
        logger.info("🌤️  Testing: 'weather in Oakland California'")
        result = await client.search(
            query="Oakland California",
            servers=["weather"]
        )
        
        if result and len(result) > 50:
            logger.success(f"✅ Got result ({len(result)} chars):")
            logger.info("\n" + "="*60)
            logger.info(result)
            logger.info("="*60 + "\n")
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
    logger.info("🚀 Starting OpenWeatherMap MCP Tests")
    logger.info("=" * 60)
    
    # Test 1: Direct MCP client
    test1_passed = await test_openweathermap_mcp()
    
    logger.info("\n" + "=" * 60)
    
    # Test 2: UnifiedMCPClient integration
    test2_passed = await test_unified_client_weather()
    
    logger.info("\n" + "=" * 60)
    logger.info("📊 Test Results:")
    logger.info(f"  OpenWeatherMap MCP: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    logger.info(f"  UnifiedMCPClient:   {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    logger.info("=" * 60)
    
    return test1_passed and test2_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

