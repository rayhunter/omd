#!/usr/bin/env python3
"""
Test script to verify News API and Weather API integration
"""

import asyncio
import sys
from pathlib import Path
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from enhanced_agent.src.unified_mcp_client import UnifiedMCPClient

async def test_news_weather():
    """Test News and Weather API integrations"""

    print("=" * 80)
    print("Testing News API & Weather API Integration")
    print("=" * 80)

    config_path = project_root / "enhanced_agent" / "config" / "mcp.json"
    print(f"\n📁 Loading config from: {config_path}")

    # Check API keys
    print("\n🔑 Checking API Keys:")
    news_key = os.getenv("NEWS_API_KEY")
    weather_key = os.getenv("OPENWEATHER_API_KEY")
    print(f"  NEWS_API_KEY: {'✅ Set' if news_key else '❌ Not set'}")
    print(f"  OPENWEATHER_API_KEY: {'✅ Set' if weather_key else '❌ Not set'}")

    try:
        client = UnifiedMCPClient(config=str(config_path))
        print("\n✅ UnifiedMCPClient initialized successfully")

        # List news and weather servers
        print("\n🌐 News & Weather Servers:")
        for server_name in client.config.servers:
            server = client.config.servers[server_name]
            if server.type.value in ["news", "weather"]:
                enabled = "✅" if server.enabled else "❌"
                print(f"  {enabled} {server_name} ({server.type.value})")
                print(f"      {server.description}")
                print(f"      Capabilities: {', '.join(server.capabilities)}")

        # Test News API
        print(f"\n{'=' * 80}")
        print("TEST 1: News API - Breaking News")
        print("=" * 80)

        news_queries = [
            "artificial intelligence",
            "technology",
            "climate change"
        ]

        for query in news_queries:
            print(f"\n📰 Searching news for: {query}")
            print("-" * 80)
            try:
                result = await client.search(query, servers=["news-api"])
                print(result)
                print("-" * 80)
            except Exception as e:
                print(f"❌ News API error: {e}")

            await asyncio.sleep(1)  # Rate limiting

        # Test Weather API
        print(f"\n{'=' * 80}")
        print("TEST 2: Weather API - Current Weather")
        print("=" * 80)

        weather_queries = [
            "London",
            "New York",
            "Tokyo",
            "San Francisco"
        ]

        for city in weather_queries:
            print(f"\n🌤️  Weather for: {city}")
            print("-" * 80)
            try:
                result = await client.search(city, servers=["weather"])
                print(result)
                print("-" * 80)
            except Exception as e:
                print(f"❌ Weather API error: {e}")

            await asyncio.sleep(0.5)

        # Test Auto-routing
        print(f"\n{'=' * 80}")
        print("TEST 3: Auto-routing for News & Weather")
        print("=" * 80)

        auto_tests = [
            ("What's the latest news about AI?", "Should route to news-api"),
            ("What's the weather in Paris?", "Should route to weather API"),
            ("Breaking news today", "Should route to news-api")
        ]

        for query, expected in auto_tests:
            print(f"\n🤖 Query: {query}")
            print(f"Expected: {expected}")
            print("-" * 80)
            try:
                result = await client.search(query)
                print(result[:300] + ("..." if len(result) > 300 else ""))
                print("-" * 80)
            except Exception as e:
                print(f"❌ Auto-routing error: {e}")

            await asyncio.sleep(1)

        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print("\n✅ NEWS API (NewsAPI.org):")
        print("  • Breaking news from 80,000+ sources worldwide")
        print("  • Real-time headlines and articles")
        print("  • Search historical articles up to 30 days")
        print("  • Free tier: 100 requests/day")

        print("\n✅ WEATHER API (OpenWeatherMap):")
        print("  • Current weather for 200,000+ cities")
        print("  • Temperature, humidity, wind, conditions")
        print("  • Free tier: 1,000 requests/day")
        print("  • Updated every 10 minutes")

        print("\n" + "=" * 80)
        print("✅ Testing complete!")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(test_news_weather())
    sys.exit(0 if success else 1)
