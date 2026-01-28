#!/usr/bin/env python3
"""
Test script to verify arXiv integration through UnifiedMCPClient
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from enhanced_agent.src.unified_mcp_client import UnifiedMCPClient

async def test_arxiv_search():
    """Test arXiv search via UnifiedMCPClient"""

    print("=" * 80)
    print("Testing arXiv Research Paper Search Integration")
    print("=" * 80)

    config_path = Path(__file__).parent / "enhanced_agent" / "config" / "mcp.json"

    try:
        client = UnifiedMCPClient(config=str(config_path))
        print("✅ UnifiedMCPClient initialized")

        # Test scientific queries that should route to arXiv
        test_queries = [
            "machine learning transformers",
            "quantum computing error correction",
            "large language models",
        ]

        for i, query in enumerate(test_queries, 1):
            print(f"\n{'=' * 80}")
            print(f"Test Query {i}: {query}")
            print("=" * 80)

            try:
                # Test with explicit arXiv server
                print(f"\n🔍 Searching arXiv directly...")
                result = await client.search(query, servers=["arxiv"])

                print(f"\n📊 arXiv Results:")
                print("-" * 80)
                print(result)
                print("-" * 80)

                # Test with auto routing (should use arXiv for scientific queries)
                print(f"\n🔍 Searching with auto routing (query contains 'research' keywords)...")
                scientific_query = f"scientific research {query}"
                result_auto = await client.search(scientific_query)

                print(f"\n📊 Auto-routed Results:")
                print("-" * 80)
                print(result_auto[:500] + ("..." if len(result_auto) > 500 else ""))
                print("-" * 80)

            except Exception as e:
                print(f"❌ Error during search: {e}")
                import traceback
                traceback.print_exc()

        print("\n" + "=" * 80)
        print("✅ arXiv testing complete!")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(test_arxiv_search())
    sys.exit(0 if success else 1)
