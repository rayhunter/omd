"""
Test Langfuse session tracking functionality.
This demonstrates how to group multiple traces into a session.
"""

import time
import uuid
from langfuse_integration import langfuse_manager, shutdown_langfuse

def test_session_tracking():
    """Test session tracking with multiple operations."""
    
    print("="*60)
    print("🧪 Testing Langfuse Session Tracking")
    print("="*60)
    
    if not langfuse_manager.enabled:
        print("\n❌ Langfuse not enabled")
        return False
    
    print("\n✅ Langfuse enabled")
    
    try:
        # Generate a unique session ID (in real app, this would come from Streamlit)
        session_id = f"session-{uuid.uuid4().hex[:8]}"
        user_id = "test-user-123"
        
        print(f"\n📌 Starting session: {session_id}")
        print(f"👤 User: {user_id}")
        
        # Set the session - all subsequent traces will be grouped
        langfuse_manager.set_session(session_id, user_id=user_id)
        
        # Simulate multiple interactions in the same session
        print("\n1️⃣  First query in session...")
        with langfuse_manager.trace_span("user_query_1", 
                                          metadata={"query_number": 1},
                                          tags=["session_test", "query"]):
            # Simulate some work
            langfuse_manager.trace_agent_step(
                step_type="think",
                input_data="What is Python?",
                output_data="Need to explain Python basics",
                metadata={"session": session_id}
            )
            time.sleep(0.1)
        
        print("   ✅ First query traced")
        
        # Second interaction in same session
        print("\n2️⃣  Second query in session...")
        with langfuse_manager.trace_span("user_query_2",
                                          metadata={"query_number": 2},
                                          tags=["session_test", "query"]):
            langfuse_manager.trace_mcp_call(
                server_name="llama-mcp",
                query="Python examples",
                response="Here are some Python examples...",
                latency_ms=150.5,
                metadata={"session": session_id}
            )
            time.sleep(0.1)
        
        print("   ✅ Second query traced")
        
        # Third interaction
        print("\n3️⃣  Third query in session...")
        with langfuse_manager.trace_span("user_query_3",
                                          metadata={"query_number": 3},
                                          tags=["session_test", "query"]):
            langfuse_manager.trace_llm_call(
                model="gpt-3.5-turbo",
                input_text="Summarize Python",
                output_text="Python is a versatile programming language...",
                metadata={"session": session_id},
                usage={"prompt_tokens": 5, "completion_tokens": 12, "total_tokens": 17}
            )
            time.sleep(0.1)
        
        print("   ✅ Third query traced")
        
        # Clear session
        print(f"\n🏁 Ending session: {session_id}")
        langfuse_manager.clear_session()
        
        # Flush traces
        print("\n📤 Flushing traces to Langfuse...")
        shutdown_langfuse()
        print("   ✅ Traces flushed")
        
        print("\n" + "="*60)
        print("✅ Session Tracking Test PASSED")
        print("="*60)
        print("\n🎯 Check your Langfuse dashboard at:")
        print("   https://us.cloud.langfuse.com")
        print(f"\n📊 Look for session: {session_id}")
        print("\n✨ You should see:")
        print("   • All 3 queries grouped together")
        print("   • Session replay showing the conversation flow")
        print("   • User ID associated with all traces")
        print("   • Timeline of interactions")
        print("\n💡 In Langfuse UI:")
        print("   1. Go to 'Sessions' in the sidebar")
        print(f"   2. Search for: {session_id}")
        print("   3. See the full conversation replay!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        shutdown_langfuse()
        return False

def test_multiple_sessions():
    """Test multiple concurrent sessions."""
    
    print("\n" + "="*60)
    print("🧪 Testing Multiple Concurrent Sessions")
    print("="*60)
    
    if not langfuse_manager.enabled:
        print("\n❌ Langfuse not enabled")
        return False
    
    try:
        # Session 1
        session1_id = f"session-alice-{uuid.uuid4().hex[:8]}"
        print(f"\n👤 Alice's session: {session1_id}")
        langfuse_manager.set_session(session1_id, user_id="alice")
        
        with langfuse_manager.trace_span("alice_query", tags=["alice"]):
            print("   ✅ Alice's query traced")
            time.sleep(0.05)
        
        # Session 2
        session2_id = f"session-bob-{uuid.uuid4().hex[:8]}"
        print(f"\n👤 Bob's session: {session2_id}")
        langfuse_manager.set_session(session2_id, user_id="bob")
        
        with langfuse_manager.trace_span("bob_query", tags=["bob"]):
            print("   ✅ Bob's query traced")
            time.sleep(0.05)
        
        # Back to Alice
        print(f"\n👤 Back to Alice's session")
        langfuse_manager.set_session(session1_id, user_id="alice")
        
        with langfuse_manager.trace_span("alice_query_2", tags=["alice"]):
            print("   ✅ Alice's second query traced")
            time.sleep(0.05)
        
        langfuse_manager.clear_session()
        shutdown_langfuse()
        
        print("\n✅ Multiple Sessions Test PASSED")
        print(f"   Alice's session: {session1_id}")
        print(f"   Bob's session: {session2_id}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        shutdown_langfuse()
        return False

if __name__ == "__main__":
    import sys
    
    # Test 1: Basic session tracking
    success1 = test_session_tracking()
    
    time.sleep(1)
    
    # Test 2: Multiple sessions
    success2 = test_multiple_sessions()
    
    if success1 and success2:
        print("\n🎉 All session tracking tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed")
        sys.exit(1)
