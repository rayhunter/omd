"""
Comprehensive test for Langfuse integration.
This will create actual traces you can see in your Langfuse dashboard.
"""

import time
from langfuse_integration import langfuse_manager, shutdown_langfuse

def test_basic_span():
    """Test basic span tracing."""
    print("\n1️⃣  Testing basic span...")
    with langfuse_manager.trace_span("test_basic_span", 
                                      metadata={"test": "basic", "version": "1.0"},
                                      tags=["test", "basic"]):
        time.sleep(0.1)  # Simulate work
        print("   ✅ Basic span created")

def test_llm_call():
    """Test LLM call tracing."""
    print("\n2️⃣  Testing LLM call tracing...")
    langfuse_manager.trace_llm_call(
        model="gpt-3.5-turbo",
        input_text="What is the capital of France?",
        output_text="The capital of France is Paris.",
        metadata={"test": "llm_call", "provider": "openai"},
        usage={"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18}
    )
    print("   ✅ LLM call traced")

def test_agent_steps():
    """Test agent step tracing."""
    print("\n3️⃣  Testing agent step tracing...")
    
    # Think step
    langfuse_manager.trace_agent_step(
        step_type="think",
        input_data="User asked about Python",
        output_data="I need to explain Python basics",
        metadata={"step": 1, "agent": "research_agent"}
    )
    
    # Act step
    langfuse_manager.trace_agent_step(
        step_type="act",
        input_data="Explain Python basics",
        output_data="Python is a high-level programming language...",
        metadata={"step": 2, "agent": "research_agent"}
    )
    
    print("   ✅ Agent steps traced")

def test_mcp_call():
    """Test MCP server call tracing."""
    print("\n4️⃣  Testing MCP call tracing...")
    langfuse_manager.trace_mcp_call(
        server_name="llama-mcp",
        query="search for AI research",
        response="Found 10 papers on AI research...",
        latency_ms=235.5,
        metadata={"test": "mcp_call", "server_type": "search"}
    )
    print("   ✅ MCP call traced")

def test_nested_traces():
    """Test nested trace spans."""
    print("\n5️⃣  Testing nested traces...")
    
    with langfuse_manager.trace_span("parent_operation", 
                                      tags=["test", "nested", "parent"]):
        print("   📦 Parent span created")
        
        with langfuse_manager.trace_span("child_operation_1",
                                          tags=["test", "nested", "child"]):
            print("   📦 Child span 1 created")
            time.sleep(0.05)
        
        with langfuse_manager.trace_span("child_operation_2",
                                          tags=["test", "nested", "child"]):
            print("   📦 Child span 2 created")
            time.sleep(0.05)
        
        print("   ✅ Nested traces created")

def test_trace_with_metadata():
    """Test trace with rich metadata."""
    print("\n6️⃣  Testing trace with rich metadata...")
    
    langfuse_manager.update_current_trace(
        name="comprehensive_test",
        user_id="test_user_123",
        session_id="test_session_456",
        tags=["test", "comprehensive", "metadata"],
        metadata={
            "environment": "test",
            "version": "1.0.0",
            "timestamp": time.time(),
            "test_type": "comprehensive"
        }
    )
    
    with langfuse_manager.trace_span("metadata_test"):
        print("   ✅ Trace with metadata created")

def test_scoring():
    """Test trace scoring."""
    print("\n7️⃣  Testing trace scoring...")
    
    with langfuse_manager.trace_span("scored_operation"):
        time.sleep(0.05)
    
    # Score the trace
    langfuse_manager.score_current_trace(
        name="quality",
        value=0.95,
        comment="Test score for comprehensive test"
    )
    
    langfuse_manager.score_current_trace(
        name="user_feedback",
        value=1.0,
        comment="Positive test feedback"
    )
    
    print("   ✅ Trace scored")

def main():
    print("="*60)
    print("🧪 Comprehensive Langfuse Integration Test")
    print("="*60)
    
    if not langfuse_manager.enabled:
        print("\n❌ Langfuse is not enabled!")
        print("Make sure your .env file has:")
        print("  LANGFUSE_PUBLIC_KEY=pk-lf-...")
        print("  LANGFUSE_SECRET_KEY=sk-lf-...")
        print("  LANGFUSE_HOST=https://us.cloud.langfuse.com")
        return
    
    print(f"\n✅ Langfuse enabled and connected")
    print(f"   Host: https://us.cloud.langfuse.com")
    
    try:
        # Run all tests
        test_basic_span()
        test_llm_call()
        test_agent_steps()
        test_mcp_call()
        test_nested_traces()
        test_trace_with_metadata()
        test_scoring()
        
        # Flush all events
        print("\n📤 Flushing events to Langfuse...")
        shutdown_langfuse()
        print("   ✅ Events flushed")
        
        print("\n" + "="*60)
        print("✅ All tests passed!")
        print("="*60)
        print("\n🎉 View your traces at:")
        print("   https://us.cloud.langfuse.com")
        print("\nYou should see:")
        print("  • Basic spans")
        print("  • LLM call with token usage")
        print("  • Agent reasoning steps")
        print("  • MCP server calls with latency")
        print("  • Nested trace hierarchy")
        print("  • Rich metadata")
        print("  • Scores on traces")
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        shutdown_langfuse()

if __name__ == "__main__":
    main()
