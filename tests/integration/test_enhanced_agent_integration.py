#!/usr/bin/env python3
"""
Test script to verify the integration between OpenManus and the enhanced agent.
"""
import asyncio
import os
from pathlib import Path

# Project root - packages should be installed via pip install -e
project_root = Path(__file__).parent.parent.parent
os.chdir(project_root)

# Now import the modules
from openmanus.agent.manus import Manus
from openmanus.logger import logger

async def test_enhanced_agent_integration():
    """Test the integration of the enhanced agent with OpenManus."""
    print("Starting enhanced agent integration test...")
    
    # Initialize the Manus agent
    agent = Manus()
    
    # Test queries that would benefit from the enhanced agent
    test_queries = [
        "Research the latest developments in quantum computing",
        "What are the current best practices for fine-tuning large language models?",
        "Can you analyze the impact of AI on healthcare in 2025?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"TESTING QUERY: {query}")
        print("-" * 80)
        
        try:
            # Run the agent with the test query
            print(f"Agent is processing your request: {query}")
            result = await agent.run(query)
            
            # Print the result
            print("\nAGENT RESPONSE:")
            print("-" * 80)
            print(result)
            print("-" * 80)
            
        except Exception as e:
            print(f"Error during agent execution: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_agent_integration())
