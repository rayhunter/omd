#!/usr/bin/env python3
"""
Simple test script to verify the enhanced agent integration.
Run this from the project root directory.
"""
import asyncio
from pathlib import Path

# Project root - packages should be installed via pip install -e
project_root = Path(__file__).parent.parent.parent

async def test_enhanced_agent():
    """Test the enhanced agent integration."""
    try:
        # Import the enhanced agent
        from enhanced_agent.src.app import run_enhanced_agent, create_agent

        # Create an agent instance for testing
        agent = create_agent()

        # Test query
        query = "What are the latest developments in AI?"
        print(f"Testing enhanced agent with query: {query}")

        # Run the enhanced agent
        result = await run_enhanced_agent(query, agent=agent)

        # Print the result
        print("\nEnhanced Agent Response:")
        print("=" * 80)
        print(result)
        print("=" * 80)
        
    except ImportError as e:
        print(f"Error importing enhanced agent: {e}")
        print("Make sure you're in the project root directory and both packages are installed.")
    except Exception as e:
        print(f"Error during enhanced agent execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_agent())
