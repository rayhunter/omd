#!/usr/bin/env python3
"""
Test script for multiple MCP servers
"""

from pathlib import Path
import asyncio
import sys

# Project root - packages should be installed via pip install -e
project_root = Path(__file__).parent.parent.parent

try:
    from enhanced_agent.src.enhanced_mcp_client import EnhancedMCPClient
    print("✅ Enhanced MCP Client imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Enhanced MCP Client: {e}")
    sys.exit(1)

def test_basic_functionality():
    """Test basic MCP client functionality"""
    print("\n🧪 Testing Enhanced MCP Client")
    print("=" * 50)
    
    # Initialize client
    client = EnhancedMCPClient()
    
    # List available servers
    print("📊 Available servers:")
    servers = client.list_servers()
    for server in servers:
        info = client.get_server_info(server)
        capabilities = info.get('capabilities', []) if info else []
        print(f"  - {server}: {', '.join(capabilities) if capabilities else 'No capabilities listed'}")
    
    return client, servers

def test_single_server(client, server_name, query):
    """Test a single server with a query"""
    print(f"\n🔍 Testing {server_name} with query: '{query}'")
    print("-" * 40)
    
    try:
        result = client.search_single_server(query, server_name)
        if result.startswith("Error:"):
            print(f"❌ {result}")
        else:
            print(f"✅ Success: {result[:200]}..." if len(result) > 200 else f"✅ Success: {result}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_multi_server(client, query, servers=None):
    """Test multiple servers with the same query"""
    print(f"\n🌐 Testing multiple servers with query: '{query}'")
    print("=" * 50)
    
    try:
        results = client.search(query, servers)
        
        for server_name, result in results.items():
            print(f"\n📡 {server_name}:")
            if result.startswith("Error:"):
                print(f"   ❌ {result}")
            else:
                # Truncate long results
                display_result = result[:150] + "..." if len(result) > 150 else result
                print(f"   ✅ {display_result}")
        
        return results
    except Exception as e:
        print(f"❌ Multi-server search failed: {e}")
        return {}

def test_auto_routing(client, queries):
    """Test automatic server routing"""
    print(f"\n🤖 Testing automatic server routing")
    print("=" * 50)
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        selected_servers = client.auto_select_servers(query)
        print(f"Auto-selected servers: {selected_servers}")

def main():
    """Main test function"""
    print("🚀 Enhanced MCP Server Testing")
    print("=" * 50)
    
    # Initialize and test basic functionality
    client, servers = test_basic_functionality()
    
    if not servers:
        print("❌ No servers available for testing")
        return
    
    # Test queries
    test_queries = [
        "What is artificial intelligence?",
        "Current weather in New York",
        "Latest research on quantum computing",
        "TSLA stock price"
    ]
    
    # Test individual servers (only test llama-mcp as it's most likely to work)
    test_single_server(client, "llama-mcp", "What is machine learning?")
    
    # Test auto routing
    test_auto_routing(client, test_queries)
    
    # Test multi-server search with available servers
    print(f"\n🔧 Testing with available servers: {servers[:3]}")  # Limit to first 3
    test_multi_server(client, "What is artificial intelligence?", servers[:3])
    
    print("\n✅ Testing completed!")
    print("\n💡 Note: Some servers may show errors if API keys are not configured.")
    print("   This is expected for services like News API, Weather API, etc.")

if __name__ == "__main__":
    main()
