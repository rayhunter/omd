#!/usr/bin/env python3
"""
Test script to verify MCP server configuration is correctly loaded
"""

from enhanced_agent.src.enhanced_mcp_client import EnhancedMCPClient

def test_mcp_servers():
    """Test that MCP servers are correctly loaded from config"""
    print("=" * 60)
    print("Testing MCP Server Configuration")
    print("=" * 60)

    # Initialize the client
    client = EnhancedMCPClient()

    # List all servers (enabled only)
    print("\n✅ Enabled MCP Servers:")
    print("-" * 60)
    servers = client.list_servers()
    for server_name in servers:
        info = client.get_server_info(server_name)
        if info:
            server_type = info.get('type', 'unknown')
            description = info.get('description', 'No description')
            capabilities = info.get('capabilities', [])
            enabled = info.get('enabled', True)

            print(f"\n📡 {server_name}")
            print(f"   Type: {server_type}")
            print(f"   Description: {description}")
            print(f"   Capabilities: {', '.join(capabilities)}")
            print(f"   Enabled: {enabled}")

    # List all servers (including disabled)
    print("\n" + "=" * 60)
    print("All Servers (including disabled):")
    print("-" * 60)
    all_servers = client.list_servers(include_disabled=True)
    disabled_servers = [s for s in all_servers if s not in servers]

    if disabled_servers:
        print(f"\n❌ Disabled Servers: {', '.join(disabled_servers)}")
        for server_name in disabled_servers:
            info = client.get_server_info(server_name)
            if info:
                print(f"   {server_name}: {info.get('description', 'No description')}")
    else:
        print("\n✅ No disabled servers")

    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"   Total servers configured: {len(all_servers)}")
    print(f"   Enabled servers: {len(servers)}")
    print(f"   Disabled servers: {len(disabled_servers)}")
    print("=" * 60)

    # Verify expected servers
    expected_enabled = ['web-search', 'llama-mcp', 'wikidata', 'dbpedia', 'arxiv', 'news-api', 'weather']
    expected_disabled = ['wikipedia']

    print("\n✅ Verification:")
    for server in expected_enabled:
        if server in servers:
            print(f"   ✓ {server} is enabled")
        else:
            print(f"   ✗ {server} is NOT enabled (expected to be enabled)")

    for server in expected_disabled:
        if server in disabled_servers:
            print(f"   ✓ {server} is disabled")
        else:
            print(f"   ✗ {server} is NOT disabled (expected to be disabled)")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_mcp_servers()
