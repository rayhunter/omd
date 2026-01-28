import asyncio
import os
import sys
from unittest.mock import MagicMock

# Ensure we can import modules
sys.path.append(os.getcwd())

from enhanced_agent.src.app import EnhancedResearchAgent
from openmanus.schema import AgentState, Message

# Mock DSPy and MCP to avoid API calls
# We need to mock dspy_mcp_integration mostly
import enhanced_agent.src.app as app_module

from unittest.mock import MagicMock, AsyncMock

# Mock the dspy_mcp integration effectively
mock_dspy = MagicMock()
mock_dspy.process_research_query = AsyncMock(return_value=MagicMock(
    direct_answer="This is a mocked answer.",
    key_insights="Insight 1",
    supporting_details="Details",
    actionable_insights="Next steps",
    query_type="general",
    main_topic="testing",
    confidence_level="high",
    gaps_identified="None",
    synthesized_context="Context",
    relevance_assessment="Relevant",
    external_info="Info"
))
mock_dspy.format_research_result.return_value = "This is a formatted mock answer."
mock_dspy.analyze_query_structure = AsyncMock(return_value={"main_topic": "test", "query_type": "test"})

# Replace the dspy_mcp instance in the module with our mock
app_module.dspy_mcp = mock_dspy

async def reproduce():
    print("🚀 Starting reproduction of looping issue...")
    
    # Initialize agent
    agent = EnhancedResearchAgent(name="test_agent")
    
    # Manually adding a user message to memory
    print("📝 Adding user message: 'Hello query'")
    agent.update_memory("user", "Hello query")
    
    # Check initial state
    print(f"Initial State: {agent.state}")
    
    # Run step 1
    print("\n--- Step 1 ---")
    should_act = await agent.think()
    print(f"Think returned: {should_act}")
    if should_act:
        result = await agent.act()
        print(f"Act result: {result}")
        # Manually perform what BaseAgent does: update step
        agent.current_step += 1
    
    print(f"\nMemory after Step 1: {[m.role for m in agent.memory.messages]}")
    
    # DEBUG: Try adding manually to see if it works
    if len(agent.memory.messages) < 2:
        print("DEBUG: Manually adding assistant response to check update_memory")
        agent.update_memory("assistant", "Manual test")
        print(f"Memory after Manual Add: {[m.role for m in agent.memory.messages]}")
    
    # Run step 2 (Research)
    print("\n--- Step 2 (Research) ---")
    should_act = await agent.think()
    print(f"Think returned: {should_act}")
    
    if should_act:
        result = await agent.act()
        print(f"Act result: {result}")
        agent.current_step += 1
    
    print(f"\nMemory after Step 2: {[m.role for m in agent.memory.messages]}")

    # Run step 3 (Should be STOP/IDLE)
    print("\n--- Step 3 (Should STOP, but will Loop) ---")
    should_act = await agent.think()
    print(f"Think returned: {should_act}")
    
    if should_act:
        print("❌ ISSUE REPRODUCED: Agent decided to act again (Looping)!")
        result = await agent.act()
        print(f"Act result: {result}")
    else:
        print("✅ ISSUE NOT REPRODUCED: Agent decided to stop.")

if __name__ == "__main__":
    asyncio.run(reproduce())
