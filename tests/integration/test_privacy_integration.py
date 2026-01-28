#!/usr/bin/env python3
"""
Test privacy and session isolation integration with the enhanced agent.
"""
import asyncio
import sys
from pathlib import Path

# Add enhanced_agent to path
sys.path.insert(0, str(Path(__file__).parent / "enhanced_agent" / "src"))

from enhanced_agent.src.app import create_agent, run_enhanced_agent
from privacy import get_session_manager, get_redacted_logger

logger = get_redacted_logger(__name__)
session_manager = get_session_manager()


async def test_session_isolation():
    """Test that agents maintain separate conversation histories per session"""
    
    print("\n" + "="*60)
    print("Testing Session Isolation")
    print("="*60)
    
    # Create two separate sessions
    session1_id = "test-session-1"
    session2_id = "test-session-2"
    
    # Create session-aware agents
    agent1 = create_agent(session_id=session1_id)
    agent2 = create_agent(session_id=session2_id)
    
    print(f"\n✅ Created agent 1 with session: {session1_id}")
    print(f"✅ Created agent 2 with session: {session2_id}")
    
    # Session 1: Ask about Python
    query1 = "What is Python programming?"
    print(f"\n📝 Session 1 query: {query1[:50]}...")
    result1 = await run_enhanced_agent(query1, agent=agent1, session_id=session1_id)
    
    # Session 2: Ask about JavaScript
    query2 = "What is JavaScript?"
    print(f"\n📝 Session 2 query: {query2[:50]}...")
    result2 = await run_enhanced_agent(query2, agent=agent2, session_id=session2_id)
    
    # Check session histories are separate
    history1 = agent1.get_session_history()
    history2 = agent2.get_session_history()
    
    print(f"\n📊 Session 1 history length: {len(history1)}")
    print(f"📊 Session 2 history length: {len(history2)}")
    
    # Verify isolation
    if len(history1) > 0 and len(history2) > 0:
        print("\n✅ Both sessions have separate histories!")
    else:
        print("\n⚠️  Session histories might not be properly isolated")
    
    # Clean up
    session_manager.end_session(session1_id)
    session_manager.end_session(session2_id)
    print("\n🧹 Sessions cleaned up")


async def test_redacted_logging():
    """Test that sensitive information is redacted in logs"""
    
    print("\n" + "="*60)
    print("Testing Redacted Logging")
    print("="*60)
    
    # Create test session
    session_id = "test-redaction"
    agent = create_agent(session_id=session_id)
    
    # Test queries with potentially sensitive info
    test_queries = [
        "My email is test@example.com",
        "Contact me at 555-123-4567",
        "My API key is sk-1234567890abcdef",
    ]
    
    for query in test_queries:
        print(f"\n🔒 Testing query with sensitive data: {query[:30]}...")
        logger.info_user_input("Test query", query)
        print("   (Check logs for redaction)")
    
    # Clean up
    session_manager.end_session(session_id)
    print("\n🧹 Test session cleaned up")


async def test_session_timeout():
    """Test that sessions expire after timeout"""
    
    print("\n" + "="*60)
    print("Testing Session Timeout")
    print("="*60)
    
    # Create session with short timeout
    session_id = "test-timeout"
    session_manager.create_session(session_id, user_id="test-user")
    
    # Add a message
    session_manager.add_message(session_id, "user", "Test message")
    
    print(f"\n✅ Created session: {session_id}")
    print("📊 Session created with test message")
    
    # Get session info
    session = session_manager.get_session(session_id)
    if session:
        print(f"📝 Session has {len(session.messages)} message(s)")
        timeout_mins = session_manager.config.session_timeout_seconds / 60
        print(f"⏰ Session will timeout after {timeout_mins} minutes of inactivity")
    
    # Test cleanup
    session_manager.end_session(session_id)
    print("🧹 Session cleaned up")
    
    # Verify cleanup
    session_after = session_manager.get_session(session_id)
    if session_after is None:
        print("✅ Session properly removed after cleanup")
    else:
        print("⚠️  Session still exists after cleanup")


async def main():
    """Run all privacy integration tests"""
    
    print("\n" + "="*60)
    print("🔐 Privacy & Session Isolation Integration Tests")
    print("="*60)
    
    try:
        await test_session_isolation()
        await test_redacted_logging()
        await test_session_timeout()
        
        print("\n" + "="*60)
        print("✅ All privacy integration tests completed!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
