#!/usr/bin/env python3
"""
Simple test to verify async MCP implementation with httpx
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_mcp_client():
    """Test basic MCP client functionality"""
    print("🧪 Testing Async MCP Client")
    print("=" * 50)

    try:
        from enhanced_agent.src.mcp_client import MCPClient
        print("✅ Successfully imported MCPClient")
    except ImportError as e:
        print(f"❌ Failed to import MCPClient: {e}")
        return False

    # Initialize client
    client = MCPClient()
    print(f"✅ Client initialized with default server: {client.default_server}")

    # List servers
    servers = client.list_servers()
    print(f"📊 Available servers: {servers}")

    # Test a simple query
    test_query = "What is Python programming?"
    print(f"\n🔍 Testing query: '{test_query}'")

    try:
        result = await client.search(test_query)
        print(f"✅ Query successful!")
        print(f"📝 Result length: {len(result)} characters")
        print(f"📄 First 200 chars: {result[:200]}...")
    except Exception as e:
        print(f"⚠️  Query failed (this is expected if Ollama is not running): {e}")

    # Test concurrent queries
    print("\n⚡ Testing concurrent queries...")
    queries = [
        "What is machine learning?",
        "What is artificial intelligence?",
        "What is deep learning?",
    ]

    try:
        tasks = [client.search(q) for q in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        print(f"📊 Concurrent query results:")
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"  Query {i+1}: ⚠️  {type(result).__name__}")
            else:
                print(f"  Query {i+1}: ✅ {len(result)} chars")
    except Exception as e:
        print(f"⚠️  Concurrent queries failed: {e}")

    # Cleanup
    await client.close()
    print("\n✅ Client closed successfully")

    return True

async def test_dspy_integration():
    """Test DSPy+MCP integration"""
    print("\n\n🧪 Testing DSPy+MCP Integration")
    print("=" * 50)

    try:
        from enhanced_agent.src.dspy_mcp_integration import DSPyMCPIntegration
        print("✅ Successfully imported DSPyMCPIntegration")
    except ImportError as e:
        print(f"❌ Failed to import DSPyMCPIntegration: {e}")
        return False

    # Initialize integration (using a small model for testing)
    try:
        integration = DSPyMCPIntegration(llm_model="gemma2:2b")
        print("✅ Integration initialized")

        # Test query analysis
        test_query = "What are the latest developments in quantum computing?"
        print(f"\n🔍 Testing query: '{test_query}'")

        analysis = await integration.analyze_query_structure(test_query)
        print(f"✅ Query analyzed successfully")
        print(f"   Topic: {analysis.get('main_topic', 'N/A')}")
        print(f"   Type: {analysis.get('query_type', 'N/A')}")
        print(f"   Search terms: {analysis.get('search_terms', [])}")

        # Test information gathering (with limited queries)
        print(f"\n📡 Testing information gathering...")
        search_terms = analysis.get('search_terms', [test_query])[:2]  # Limit to 2
        gathered = await integration.gather_information(search_terms)
        print(f"✅ Information gathered: {len(gathered)} characters")

    except Exception as e:
        print(f"⚠️  Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

async def main():
    """Main test runner"""
    print("🚀 Async MCP Implementation Test Suite")
    print("=" * 60)
    print()

    # Test MCP client
    mcp_success = await test_mcp_client()

    # Test DSPy integration
    integration_success = await test_dspy_integration()

    # Summary
    print("\n\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"  MCP Client: {'✅ PASS' if mcp_success else '❌ FAIL'}")
    print(f"  DSPy Integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
    print("=" * 60)

    print("\n💡 Notes:")
    print("  - Query failures are expected if Ollama is not running")
    print("  - Start Ollama with: ollama serve")
    print("  - Install models with: ollama pull gemma2:2b")

if __name__ == "__main__":
    asyncio.run(main())
