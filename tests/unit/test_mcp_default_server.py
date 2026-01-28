#!/usr/bin/env python3
"""
Test script to verify UnifiedMCPClient.default_server property works correctly
"""

import sys
from pathlib import Path

# Add enhanced_agent to path
sys.path.insert(0, str(Path(__file__).parent / "enhanced_agent"))

try:
    from src.unified_mcp_client import UnifiedMCPClient

    print("🧪 Testing UnifiedMCPClient.default_server property...")

    # Create client
    client = UnifiedMCPClient()

    # Test accessing default_server property
    default_server = client.default_server
    print(f"✅ Successfully accessed default_server: {default_server}")

    # Verify it matches config
    assert default_server == client.config.default_server
    print(f"✅ Property matches config value")

    # Test list_servers
    servers = client.list_servers()
    print(f"✅ Available servers: {servers}")

    print("\n✅ All tests passed! The MCP status check should work now.")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
