"""
Simple script to verify Langfuse traces are appearing on the dashboard.
Run this and then check your dashboard immediately.
"""
import time
from langfuse_integration import langfuse_manager, shutdown_langfuse

print("="*70)
print("🔍 Langfuse Dashboard Verification Test")
print("="*70)

if not langfuse_manager.enabled:
    print("\n❌ Langfuse is not enabled. Check your configuration.")
    exit(1)

print(f"\n✅ Langfuse connected to: https://us.cloud.langfuse.com")

# Create a unique, easily identifiable trace
test_id = f"test_{int(time.time())}"
print(f"\n📊 Creating test trace with ID: {test_id}")

with langfuse_manager.trace_span(
    name=f"verification_test_{test_id}",
    metadata={"test_type": "dashboard_verification", "timestamp": test_id},
    tags=["verification", "dashboard_test"]
):
    print("   ✅ Trace created")

    # Add a generation (LLM call)
    langfuse_manager.trace_llm_call(
        model="test-model",
        input_text="This is a verification test",
        output_text="This trace should appear on your dashboard",
        metadata={"verification_id": test_id},
        usage={"input": 5, "output": 7, "total": 12}
    )
    print("   ✅ LLM call logged")

    # Add metadata to make it easy to find
    langfuse_manager.update_current_trace(
        name=f"DASHBOARD_TEST_{test_id}",
        tags=["EASY_TO_FIND", "VERIFICATION"],
        metadata={
            "search_for_this": "DASHBOARD_VERIFICATION_TEST",
            "test_id": test_id,
            "instructions": "If you see this on your dashboard, the integration is working!"
        }
    )
    print("   ✅ Trace metadata updated")

print("\n📤 Flushing to Langfuse...")
shutdown_langfuse()
print("   ✅ Data sent to Langfuse")

print("\n" + "="*70)
print("✅ TEST COMPLETE!")
print("="*70)
print("\n🔍 Now check your Langfuse dashboard:")
print("   https://us.cloud.langfuse.com")
print("\n   Look for:")
print(f"   • Trace name: DASHBOARD_TEST_{test_id}")
print(f"   • Tags: EASY_TO_FIND, VERIFICATION")
print(f"   • Test ID: {test_id}")
print("\n   If you see this trace, the integration is working correctly! ✅")
print("   If not, there may be an authentication or network issue. ❌")
print("="*70)
