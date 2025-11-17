#!/usr/bin/env python3
"""
Demo script showing the enhanced research agent in action.
"""

import asyncio
import sys
import os
from pathlib import Path

async def demo_research_agent():
    """Demonstrate the research agent with sample queries."""
    
    print("🎬 Enhanced Research Agent Demo")
    print("=" * 50)
    
    # Sample queries to demonstrate different capabilities
    demo_queries = [
        "What is quantum computing?",
        "How can small businesses use AI?", 
        "What are the benefits of renewable energy?"
    ]
    
    try:
        # Import the enhanced agent (may fail if dependencies missing)
        from enhanced_agent.src.app import run_enhanced_agent, create_agent

        # Create an agent instance for the demo
        agent = create_agent()

        print("✅ Enhanced research agent loaded successfully")
        print("\n🔍 Running demo queries...\n")

        for i, query in enumerate(demo_queries, 1):
            print(f"📝 Demo Query {i}: {query}")
            print("=" * 40)

            try:
                # Run the query through our enhanced agent
                result = await run_enhanced_agent(query, agent=agent)
                
                # Show condensed results
                print("✅ Query processed successfully!")
                print(f"📏 Response length: {len(result)} characters")
                
                # Show first few lines of the response
                lines = result.split('\n')[:8]
                preview = '\n'.join(lines)
                print("\n📋 Response Preview:")
                print("-" * 25)
                print(preview)
                if len(result.split('\n')) > 8:
                    print("... (truncated)")
                    
            except Exception as e:
                print(f"❌ Error processing query: {e}")
                
            print("\n" + "="*50 + "\n")
            
        print("🎉 Demo completed successfully!")
        
    except ImportError as e:
        print(f"❌ Could not import enhanced agent: {e}")
        print("\n💡 To fix this:")
        print("1. Install dependencies: pip install dspy-ai>=2.0.0")
        print("2. Make sure OpenManus is properly set up")
        print("3. Check that enhanced_agent package is installed")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

async def interactive_demo():
    """Run interactive demo where user can ask questions."""

    print("\n🎮 Interactive Demo Mode")
    print("=" * 30)
    print("Ask the research agent any question!")
    print("Type 'quit' to exit\n")

    try:
        from enhanced_agent.src.app import run_enhanced_agent, create_agent

        # Create an agent instance for interactive mode
        agent = create_agent()

        while True:
            user_query = input("🤔 Your question: ")

            if user_query.lower() in ['quit', 'exit', 'q']:
                print("👋 Thanks for trying the enhanced research agent!")
                break

            if not user_query.strip():
                print("Please enter a question!")
                continue

            print(f"\n🚀 Processing: {user_query}")
            print("-" * 30)

            try:
                result = await run_enhanced_agent(user_query, agent=agent)
                print("\n📋 Research Agent Response:")
                print("=" * 35)
                print(result)
                print("\n" + "="*50 + "\n")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                print("Try another question or type 'quit' to exit\n")
                
    except ImportError as e:
        print(f"❌ Interactive mode unavailable: {e}")

if __name__ == "__main__":
    print("🚀 Enhanced Research Agent Demo Script")
    print("This demonstrates the OpenManus + DSPy + MCP integration\n")
    
    mode = input("Choose mode: (1) Demo with sample queries, (2) Interactive, (3) Both [1]: ").strip()
    
    if mode == "" or mode == "1":
        asyncio.run(demo_research_agent())
    elif mode == "2":
        asyncio.run(interactive_demo())
    elif mode == "3":
        asyncio.run(demo_research_agent())
        asyncio.run(interactive_demo())
    else:
        print("Invalid choice. Running demo mode...")
        asyncio.run(demo_research_agent())