#!/usr/bin/env python3
"""
Test script for the DSPy+MCP+OpenManus integration.

This script tests the enhanced research agent with actual DSPy structured reasoning.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add enhanced_agent to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "enhanced_agent"))

async def test_dspy_integration():
    """Test the DSPy integration with sample queries."""
    
    print("🧪 Testing DSPy+MCP+OpenManus Integration")
    print("=" * 50)
    
    try:
        # Import the enhanced agent
        from enhanced_agent.src.app import run_enhanced_agent, create_agent, dspy_mcp

        # Create an agent instance for testing
        agent = create_agent()

        # Check integration status
        if dspy_mcp:
            print("✅ DSPy+MCP integration loaded successfully")
            print(f"📊 MCP servers: {dspy_mcp.mcp_client.list_servers()}")
        else:
            print("⚠️  DSPy integration not available, testing basic MCP mode")

        print("\n🔍 Running test queries...\n")

        # Test queries of different types
        test_queries = [
            "What is machine learning?",
            "How does photosynthesis work?",
            "What are the latest developments in quantum computing?"
        ]

        for i, query in enumerate(test_queries, 1):
            print(f"📝 Test Query {i}: {query}")
            print("-" * 30)

            try:
                result = await run_enhanced_agent(query, agent=agent)
                print("✅ Query processed successfully")
                print(f"Response length: {len(result)} characters")
                print(f"Preview: {result[:200]}...")

            except Exception as e:
                print(f"❌ Error processing query: {e}")

            print("\n" + "="*50 + "\n")
            
        print("🏁 Integration test completed")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure enhanced_agent dependencies are installed:")
        print("  pip install dspy-ai>=2.0.0")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


async def test_dspy_modules_directly():
    """Test DSPy modules directly without OpenManus integration."""
    
    print("\n🔬 Testing DSPy Modules Directly")
    print("=" * 40)
    
    try:
        from enhanced_agent.src.dspy_modules import QuickAnalysis
        import dspy
        
        # Configure DSPy with a simple model (you may need to adjust this)
        try:
            # This might fail if OpenAI API key is not set
            lm = dspy.OpenAI(model="gpt-3.5-turbo", max_tokens=500, temperature=0.1)
            dspy.settings.configure(lm=lm)
            print("✅ DSPy configured with OpenAI")
        except:
            print("⚠️  Could not configure DSPy with OpenAI, skipping direct tests")
            return
        
        # Test the quick analysis module
        analyzer = QuickAnalysis()
        
        test_query = "What are the benefits of renewable energy?"
        print(f"📊 Analyzing: {test_query}")
        
        result = analyzer(user_query=test_query)
        
        print("✅ DSPy Analysis Results:")
        print(f"  Topic: {result['main_topic']}")
        print(f"  Type: {result['query_type']}")
        print(f"  Search terms: {result['search_terms']}")
        print(f"  Information needs: {result['information_needs']}")
        
    except Exception as e:
        print(f"❌ DSPy module test failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting Enhanced Research Agent Tests\n")
    
    # Run integration test
    asyncio.run(test_dspy_integration())
    
    # Run direct DSPy module test
    asyncio.run(test_dspy_modules_directly())
    
    print("\n✅ All tests completed!")