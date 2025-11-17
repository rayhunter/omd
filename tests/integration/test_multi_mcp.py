#!/usr/bin/env python3
"""
Test script for multiple MCP servers (async version)
"""

from pathlib import Path
import asyncio
import sys

# Project root - packages should be installed via pip install -e
project_root = Path(__file__).parent.parent.parent

try:
    from enhanced_agent.src.mcp_client import MCPClient
    print("✅ MCP Client imported successfully")
except ImportError as e:
    print(f"❌ Failed to import MCP Client: {e}")
    sys.exit(1)

def test_basic_functionality():
    """Test basic MCP client functionality"""
    print("\n🧪 Testing MCP Client")
    print("=" * 50)

    # Initialize client
    client = MCPClient()

    # List available servers
    print("📊 Available servers:")
    servers = client.list_servers()
    for server in servers:
        info = client.get_server_info(server)
        print(f"  - {server}: {info}")

    return client, servers

async def test_single_server(client, server_name, query):
    """Test a single server with a query (async)"""
    print(f"\n🔍 Testing {server_name} with query: '{query}'")
    print("-" * 40)

    try:
        result = await client.search(query, server_name)
        if result.startswith("Error:"):
            print(f"❌ {result}")
        else:
            print(f"✅ Success: {result[:200]}..." if len(result) > 200 else f"✅ Success: {result}")
    except Exception as e:
        print(f"❌ Exception: {e}")

async def test_concurrent_queries(client, queries):
    """Test concurrent queries with semaphore-based rate limiting"""
    print(f"\n⚡ Testing concurrent queries")
    print("=" * 50)

    async def query_and_report(query, index):
        print(f"🔄 Starting query {index+1}: '{query[:50]}...'")
        result = await client.search(query)
        print(f"✅ Query {index+1} complete: {len(result)} chars")
        return result

    try:
        tasks = [query_and_report(query, i) for i, query in enumerate(queries)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        print(f"\n📊 Results summary:")
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"  Query {i+1}: ❌ Failed with {type(result).__name__}")
            else:
                print(f"  Query {i+1}: ✅ {len(result)} characters")

        return results
    except Exception as e:
        print(f"❌ Concurrent query test failed: {e}")
        return []

async def main():
    """Main test function (async)"""
    print("🚀 Async MCP Client Testing")
    print("=" * 50)

    # Initialize and test basic functionality
    client, servers = test_basic_functionality()

    if not servers:
        print("❌ No servers available for testing")
        return

    # Test queries
    test_queries = [
        "What is artificial intelligence?",
        "What is machine learning?",
        "What is deep learning?",
    ]

    # Test single server query
    await test_single_server(client, "llama-mcp", "What is machine learning?")

    # Test concurrent queries
    await test_concurrent_queries(client, test_queries)

    # Cleanup
    await client.close()

    print("\n✅ Testing completed!")
    print("\n💡 Note: Some servers may show errors if they are not running.")
    print("   This is expected if Ollama or other services are not available.")

if __name__ == "__main__":
    asyncio.run(main())
