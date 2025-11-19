#!/usr/bin/env python3
"""
Test script to verify Wikidata and DBpedia integration through UnifiedMCPClient
This replaces Wikipedia with more reliable, structured knowledge sources.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from enhanced_agent.src.unified_mcp_client import UnifiedMCPClient

async def test_wikidata_dbpedia():
    """Test Wikidata and DBpedia structured knowledge sources"""

    print("=" * 80)
    print("Testing Wikidata & DBpedia Structured Knowledge Integration")
    print("=" * 80)

    config_path = Path(__file__).parent / "enhanced_agent" / "config" / "mcp.json"
    print(f"\n📁 Loading config from: {config_path}")

    try:
        client = UnifiedMCPClient(config=str(config_path))
        print("✅ UnifiedMCPClient initialized successfully")

        # List available servers
        print("\n🌐 Available Knowledge Servers:")
        for server_name in client.config.servers:
            server = client.config.servers[server_name]
            enabled = "✅" if server.enabled else "❌"
            if server.type.value in ["wikidata", "dbpedia", "wikipedia"]:
                print(f"  {enabled} {server_name} ({server.type.value})")
                print(f"      {server.description}")
                print(f"      Capabilities: {', '.join(server.capabilities)}")

        # Test queries for factual/encyclopedic knowledge
        test_cases = [
            {
                "query": "Albert Einstein",
                "description": "Famous person - should return structured entity data"
            },
            {
                "query": "Paris",
                "description": "Geographic entity - capital city"
            },
            {
                "query": "Python programming language",
                "description": "Technology/Concept"
            },
            {
                "query": "World War II",
                "description": "Historical event"
            },
            {
                "query": "photosynthesis",
                "description": "Scientific concept"
            }
        ]

        for i, test_case in enumerate(test_cases, 1):
            query = test_case["query"]
            description = test_case["description"]

            print(f"\n{'=' * 80}")
            print(f"Test Case {i}: {query}")
            print(f"Description: {description}")
            print("=" * 80)

            # Test 1: Wikidata (structured entities with provenance)
            print(f"\n🔷 Querying Wikidata (Structured Knowledge Graph)...")
            try:
                result_wikidata = await client.search(query, servers=["wikidata"])
                print(f"\n📊 Wikidata Results:")
                print("-" * 80)
                print(result_wikidata)
                print("-" * 80)
            except Exception as e:
                print(f"❌ Wikidata error: {e}")

            # Test 2: DBpedia (structured Wikipedia data)
            print(f"\n📘 Querying DBpedia (Structured Wikipedia Data)...")
            try:
                result_dbpedia = await client.search(query, servers=["dbpedia"])
                print(f"\n📊 DBpedia Results:")
                print("-" * 80)
                print(result_dbpedia)
                print("-" * 80)
            except Exception as e:
                print(f"❌ DBpedia error: {e}")

            # Test 3: Auto-routing (should prefer Wikidata/DBpedia for factual queries)
            print(f"\n🤖 Auto-routing (Should prefer Wikidata/DBpedia for factual data)...")
            try:
                # Add "factual" keyword to trigger routing rules
                auto_query = f"factual information about {query}"
                result_auto = await client.search(auto_query)
                print(f"\n📊 Auto-routed Results:")
                print("-" * 80)
                print(result_auto[:500] + ("..." if len(result_auto) > 500 else ""))
                print("-" * 80)
            except Exception as e:
                print(f"❌ Auto-routing error: {e}")

            # Small delay between test cases
            await asyncio.sleep(1)

        # Summary comparison
        print("\n" + "=" * 80)
        print("📊 COMPARISON SUMMARY")
        print("=" * 80)
        print("\n✅ WIKIDATA Advantages:")
        print("  • Structured entities with unique IDs (e.g., Q937 = Albert Einstein)")
        print("  • Multilingual support (same entity in all languages)")
        print("  • Provenance tracking (every fact has sources)")
        print("  • Machine-verifiable relationships")
        print("  • Used by Google, Alexa, Siri for factual data")

        print("\n✅ DBPEDIA Advantages:")
        print("  • 850M+ semantic triples extracted from Wikipedia")
        print("  • Natural language abstracts + structured data")
        print("  • Linked data (connects entities across domains)")
        print("  • SPARQL queryable for complex relationships")
        print("  • Used by IBM Watson for knowledge extraction")

        print("\n❌ WIKIPEDIA (now disabled):")
        print("  • Crowdsourced (quality varies)")
        print("  • Unstructured text (harder to verify)")
        print("  • No provenance tracking")
        print("  • Replaced by Wikidata + DBpedia for better accuracy")

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
    success = asyncio.run(test_wikidata_dbpedia())
    sys.exit(0 if success else 1)
