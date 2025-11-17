import sys
from pathlib import Path

# Add src to Python path
# sys.path.append(str(Path("src")))

# # Add OpenManus to path
# sys.path.append(str(Path("../OpenManus")))

from src.app import run_enhanced_agent, create_agent
import asyncio

if __name__ == "__main__":
    print("🚀 Enhanced Research Agent with MCP Integration")
    print("-" * 50)
    print("This agent combines:")
    print("1. DSPy for structured reasoning")
    print("2. MCP for real-time information gathering")
    print("3. ReAct pattern for step-by-step processing")
    print("-" * 50)

    # Create a session-scoped agent instance
    agent = create_agent()

    while True:
        try:
            user_input = input("\nEnter your request (or 'quit' to exit): ")
            if user_input.lower() in ['quit', 'exit']:
                break

            result = asyncio.run(run_enhanced_agent(user_input, agent=agent))
            print("\nEnhanced Agent Response:")
            print(result)

        except KeyboardInterrupt:
            print("\nGracefully shutting down...")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Try another request or 'quit' to exit") 