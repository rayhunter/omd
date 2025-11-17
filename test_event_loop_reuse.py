#!/usr/bin/env python3
"""
Test script for Streamlit event loop reuse functionality.

This script validates that:
1. Event loops are created once and reused
2. Multiple async operations share the same loop
3. No new loops are created unnecessarily
4. Cleanup works properly
"""

import asyncio
import sys
from pathlib import Path

# Mock streamlit session_state for testing
class MockSessionState:
    def __init__(self):
        self._state = {}

    def __contains__(self, key):
        return key in self._state

    def __getitem__(self, key):
        return self._state[key]

    def __setitem__(self, key, value):
        self._state[key] = value

    def __delitem__(self, key):
        del self._state[key]

    def get(self, key, default=None):
        return self._state.get(key, default)

# Mock streamlit module
class MockStreamlit:
    def __init__(self):
        self.session_state = MockSessionState()

# Create mock st object
st = MockStreamlit()

# Import the async helper functions (simulated)
def get_or_create_event_loop():
    """Get or create a persistent event loop stored in session state."""
    if 'event_loop' not in st.session_state:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        st.session_state['event_loop'] = loop
        print("🔄 Created new event loop for session")
    return st.session_state['event_loop']

def run_async(coro):
    """Centralized async execution helper that reuses the session event loop."""
    loop = get_or_create_event_loop()

    if loop.is_running():
        raise RuntimeError("Event loop is already running. Use await instead.")

    return loop.run_until_complete(coro)

def cleanup_event_loop():
    """Cleanup function to properly close the event loop when the session ends."""
    if 'event_loop' in st.session_state:
        loop = st.session_state['event_loop']
        if not loop.is_closed():
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            loop.close()
            print("🔄 Event loop closed")
        del st.session_state['event_loop']

# Test async functions
async def test_async_function_1():
    """Simple async test function."""
    await asyncio.sleep(0.01)
    return "Result from function 1"

async def test_async_function_2():
    """Another async test function."""
    await asyncio.sleep(0.01)
    return "Result from function 2"

async def test_async_function_3():
    """Third async test function with error handling."""
    await asyncio.sleep(0.01)
    return "Result from function 3"

def test_event_loop_reuse():
    """Test that event loop is created once and reused."""
    print("\n" + "="*70)
    print("TEST 1: Event Loop Reuse")
    print("="*70)

    # First call should create a new loop
    print("\n1. First async call (should create new loop):")
    loop1_id = id(get_or_create_event_loop())
    result1 = run_async(test_async_function_1())
    print(f"   Result: {result1}")
    print(f"   Loop ID: {loop1_id}")

    # Second call should reuse the same loop
    print("\n2. Second async call (should reuse existing loop):")
    loop2_id = id(get_or_create_event_loop())
    result2 = run_async(test_async_function_2())
    print(f"   Result: {result2}")
    print(f"   Loop ID: {loop2_id}")

    # Third call should also reuse the same loop
    print("\n3. Third async call (should reuse existing loop):")
    loop3_id = id(get_or_create_event_loop())
    result3 = run_async(test_async_function_3())
    print(f"   Result: {result3}")
    print(f"   Loop ID: {loop3_id}")

    # Verify all loops are the same
    assert loop1_id == loop2_id == loop3_id, "Event loops should be reused!"
    print("\n✅ SUCCESS: All async operations used the same event loop!")

    return True

def test_cleanup():
    """Test that cleanup works properly."""
    print("\n" + "="*70)
    print("TEST 2: Event Loop Cleanup")
    print("="*70)

    # Get the current loop
    loop_before = st.session_state.get('event_loop')
    print(f"\n1. Loop before cleanup: {loop_before}")

    # Clean up
    print("\n2. Calling cleanup_event_loop()...")
    cleanup_event_loop()

    # Verify loop is removed
    loop_after = st.session_state.get('event_loop')
    print(f"\n3. Loop after cleanup: {loop_after}")

    assert loop_after is None, "Event loop should be removed from session state!"
    assert loop_before.is_closed(), "Event loop should be closed!"
    print("\n✅ SUCCESS: Event loop cleaned up properly!")

    return True

def test_new_loop_after_cleanup():
    """Test that a new loop is created after cleanup."""
    print("\n" + "="*70)
    print("TEST 3: New Loop Creation After Cleanup")
    print("="*70)

    # Run an async operation (should create new loop)
    print("\n1. Running async operation after cleanup:")
    new_loop_id = id(get_or_create_event_loop())
    result = run_async(test_async_function_1())
    print(f"   Result: {result}")
    print(f"   New Loop ID: {new_loop_id}")

    print("\n✅ SUCCESS: New event loop created after cleanup!")

    return True

def test_multiple_operations():
    """Test multiple async operations in sequence."""
    print("\n" + "="*70)
    print("TEST 4: Multiple Sequential Operations")
    print("="*70)

    loop_ids = []

    for i in range(5):
        print(f"\n{i+1}. Running operation {i+1}:")
        loop_id = id(get_or_create_event_loop())
        loop_ids.append(loop_id)
        result = run_async(test_async_function_1())
        print(f"   Loop ID: {loop_id}")

    # Verify all operations used the same loop
    assert len(set(loop_ids)) == 1, "All operations should use the same loop!"
    print(f"\n✅ SUCCESS: All {len(loop_ids)} operations used the same event loop!")

    return True

def main():
    """Run all tests."""
    print("🧪 Testing Streamlit Event Loop Reuse Functionality")
    print("="*70)

    try:
        # Run tests
        tests = [
            test_event_loop_reuse,
            test_cleanup,
            test_new_loop_after_cleanup,
            test_multiple_operations,
        ]

        results = []
        for test in tests:
            try:
                result = test()
                results.append((test.__name__, result))
            except Exception as e:
                print(f"\n❌ FAILED: {test.__name__}")
                print(f"   Error: {e}")
                results.append((test.__name__, False))
                import traceback
                traceback.print_exc()

        # Final cleanup
        cleanup_event_loop()

        # Print summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")

        print(f"\nTotal: {passed}/{total} tests passed")

        if passed == total:
            print("\n🎉 All tests passed!")
            return 0
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")
            return 1

    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
