#!/usr/bin/env python3
"""
Quick test to verify Langfuse is actually sending data to the dashboard.
"""

from langfuse_integration import langfuse_manager
import time

print("=" * 60)
print("Langfuse Data Send Test")
print("=" * 60)

# Check configuration
print(f"\n✓ Langfuse enabled: {langfuse_manager.enabled}")
print(f"✓ Client available: {langfuse_manager.client is not None}")

if not langfuse_manager.enabled:
    print("\n❌ Langfuse not enabled. Check your .env file.")
    exit(1)

# Set session info
session_id = f"test-session-{int(time.time())}"
langfuse_manager.set_session(session_id, user_id="test-user")
print(f"\n✓ Session ID: {session_id}")

# Create a test trace
print("\n📤 Sending test trace to Langfuse...")
with langfuse_manager.trace_span(
    "test_trace_verification",
    metadata={
        "test_type": "manual_verification",
        "timestamp": time.time()
    },
    tags=["test", "verification"]
) as span:
    print("  ✓ Inside trace span")

    # Test LLM call tracking
    langfuse_manager.trace_llm_call(
        model="test-model",
        input_text="This is a test query",
        output_text="This is a test response",
        metadata={"test": True},
        usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
    )
    print("  ✓ LLM call traced")

    # Test agent step tracking
    langfuse_manager.trace_agent_step(
        step_type="think",
        input_data="Test input",
        output_data="Test output",
        metadata={"step": 1}
    )
    print("  ✓ Agent step traced")

print("\n⏳ Flushing events to Langfuse...")
langfuse_manager.shutdown()

print("\n" + "=" * 60)
print("✅ Test complete!")
print("=" * 60)
print("\n📊 Check your Langfuse dashboard:")
print("   https://us.cloud.langfuse.com")
print(f"\n🔍 Search for session: {session_id}")
print("   You should see:")
print("   - 1 trace named 'test_trace_verification'")
print("   - 1 LLM call with test-model")
print("   - 1 agent step with type 'think'")
print("\n💡 If you don't see data, check:")
print("   1. Your Langfuse credentials are correct")
print("   2. Your project selection in the dashboard")
print("   3. Wait 10-30 seconds for data to appear")
print("=" * 60)
