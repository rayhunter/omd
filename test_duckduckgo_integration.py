#!/usr/bin/env python3
"""
Test script to verify DuckDuckGo web search is working through UnifiedMCPClient
"""

import asyncio
import sys
from pathlib import Path

# Add enhanced_agent to path
sys.path.insert(0, str(Path(__file__).parent))

from enhanced_agent.src.unified_mcp_client import UnifiedMCPClient

async def test_duckduckgo_search():
    """Test DuckDuckGo web search via UnifiedMCPClient"""

    print("=" * 80)
    print("Testing DuckDuckGo Web Search Integration")
    print("=" * 80)

    # Initialize client with the enhanced_agent config
    config_path = Path(__file__).parent / "enhanced_agent" / "config" / "mcp.json"
    print(f"\n📁 Loading config from: {config_path}")

    try:
        client = UnifiedMCPClient(config=str(config_path))
        print("✅ UnifiedMCPClient initialized successfully")

        # List available servers
        print("\n🌐 Available servers:")
        for server_name in client.config.servers:
            server = client.config.servers[server_name]
            enabled = "✅" if server.enabled else "❌"
            print(f"  {enabled} {server_name} ({server.type.value}): {server.description}")

        # Check what attribute name is actually used
        default_server = getattr(client.config, 'default_server',
                                 getattr(client.config, 'default_mcp_server', 'unknown'))
        print(f"\n🎯 Default server: {default_server}")
        print(f"📋 Routing strategy: {client.config.server_selection_strategy.value}")

        # Test queries
        test_queries = [
            "What is the capital of France?",
            "Python programming language",
            "artificial intelligence recent developments"
        ]

        for i, query in enumerate(test_queries, 1):
            print(f"\n{'=' * 80}")
            print(f"Test Query {i}: {query}")
            print("=" * 80)

            try:
                # Test with auto routing (should select web-search for general queries)
                print(f"\n🔍 Searching with auto routing...")
                result = await client.search(query)

                print(f"\n📊 Result (length: {len(result)} chars):")
                print("-" * 80)
                print(result[:500] + ("..." if len(result) > 500 else ""))
                print("-" * 80)

                # Test with explicit web-search server
                print(f"\n🔍 Searching with explicit web-search server...")
                result_web = await client.search(query, servers=["web-search"])

                print(f"\n📊 Web Search Result (length: {len(result_web)} chars):")
                print("-" * 80)
                print(result_web[:500] + ("..." if len(result_web) > 500 else ""))
                print("-" * 80)

            except Exception as e:
                print(f"❌ Error during search: {e}")
                import traceback
                traceback.print_exc()

        print("\n" + "=" * 80)
        print("✅ Testing complete!")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error initializing client: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(test_duckduckgo_search())
    sys.exit(0 if success else 1)
