#!/usr/bin/env python3
"""
Test script to verify the integration between OpenManus and the enhanced agent.
"""
import asyncio
from pathlib import Path

# Project root - packages should be installed via pip install -e
project_root = Path(__file__).parent.parent.parent

async def test_enhanced_agent():
    """Test the enhanced agent integration."""
    try:
        print("Testing enhanced agent integration...")
        
        # Import the enhanced agent tool
        from openmanus.tool.enhanced_agent_tool import EnhancedAgentTool
        
        # Initialize the tool
        tool = EnhancedAgentTool()
        
        # Test query
        query = "What are the latest developments in AI?"
        print(f"\nSending query to enhanced agent: {query}")
        
        # Run the tool
        result = await tool.arun(query)
        
        # Print the result
        print("\nEnhanced Agent Response:")
        print("=" * 80)
        print(result)
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"Error during enhanced agent execution: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_enhanced_agent())
