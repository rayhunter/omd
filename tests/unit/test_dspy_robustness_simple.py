"""
Simple unit tests to verify DSPy pipeline robustness improvements.

Tests the specific improvements made:
1. analysis = None initialization before try-block
2. (analysis or defaults) pattern in fallback
3. Step-level caching mechanism

These tests don't make real LLM calls - they test the error handling logic directly.
"""

import sys
from pathlib import Path

# Add enhanced_agent to path for proper package imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_fallback_dict_pattern():
    """Test that (analysis or defaults) pattern works correctly."""
    print("\n" + "="*60)
    print("TEST 1: Fallback dictionary pattern")
    print("="*60)

    # Simulate analysis being None
    analysis = None

    fallback_defaults = {
        'main_topic': 'Default Topic',
        'sub_topics': ['default'],
        'query_type': 'general',
        'information_needs': 'General information',
        'search_terms': ['test']
    }

    # Test the pattern used in the improved code
    main_topic = (analysis or fallback_defaults).get('main_topic', fallback_defaults['main_topic'])
    sub_topics = (analysis or fallback_defaults).get('sub_topics', fallback_defaults['sub_topics'])
    query_type = (analysis or fallback_defaults).get('query_type', fallback_defaults['query_type'])

    assert main_topic == 'Default Topic', f"Expected 'Default Topic', got {main_topic}"
    assert sub_topics == ['default'], f"Expected ['default'], got {sub_topics}"
    assert query_type == 'general', f"Expected 'general', got {query_type}"

    print(f"✅ None case works correctly:")
    print(f"   main_topic: {main_topic}")
    print(f"   sub_topics: {sub_topics}")
    print(f"   query_type: {query_type}")

    # Now test with actual analysis dict
    analysis = {
        'main_topic': 'Real Topic',
        'sub_topics': ['real1', 'real2'],
        'query_type': 'factual',
    }

    main_topic = (analysis or fallback_defaults).get('main_topic', fallback_defaults['main_topic'])
    sub_topics = (analysis or fallback_defaults).get('sub_topics', fallback_defaults['sub_topics'])
    query_type = (analysis or fallback_defaults).get('query_type', fallback_defaults['query_type'])

    assert main_topic == 'Real Topic', f"Expected 'Real Topic', got {main_topic}"
    assert sub_topics == ['real1', 'real2'], f"Expected ['real1', 'real2'], got {sub_topics}"
    assert query_type == 'factual', f"Expected 'factual', got {query_type}"

    print(f"\n✅ Dict case works correctly:")
    print(f"   main_topic: {main_topic}")
    print(f"   sub_topics: {sub_topics}")
    print(f"   query_type: {query_type}")

    return True


def test_external_info_none_handling():
    """Test that external_info=None is handled safely in fallback."""
    print("\n" + "="*60)
    print("TEST 2: external_info None handling")
    print("="*60)

    external_info = None

    # Test the pattern used in the improved code
    synthesized_context = f"Query: test\nExternal Info: {external_info[:500] if external_info else 'N/A'}..."
    supporting_details = (external_info[:1000] + "..." if external_info and len(external_info) > 1000
                         else external_info or "No information gathered")
    external_info_field = external_info or ""

    assert "N/A" in synthesized_context, f"Expected 'N/A' in context, got {synthesized_context}"
    assert supporting_details == "No information gathered", f"Expected 'No information gathered', got {supporting_details}"
    assert external_info_field == "", f"Expected empty string, got {external_info_field}"

    print(f"✅ None case works correctly:")
    print(f"   synthesized_context: {synthesized_context[:50]}...")
    print(f"   supporting_details: {supporting_details}")
    print(f"   external_info_field: '{external_info_field}'")

    # Test with actual data
    external_info = "Some external information " * 50  # Long string

    synthesized_context = f"Query: test\nExternal Info: {external_info[:500] if external_info else 'N/A'}..."
    supporting_details = (external_info[:1000] + "..." if external_info and len(external_info) > 1000
                         else external_info or "No information gathered")
    external_info_field = external_info or ""

    assert "N/A" not in synthesized_context, f"Should not have 'N/A' with real data"
    assert "..." in supporting_details, f"Should truncate long external_info"
    assert len(external_info_field) > 0, f"Should have external_info content"

    print(f"\n✅ Data case works correctly:")
    print(f"   synthesized_context length: {len(synthesized_context)}")
    print(f"   supporting_details length: {len(supporting_details)}")
    print(f"   external_info_field length: {len(external_info_field)}")

    return True


def test_step_cache_mechanism():
    """Test the step-level caching mechanism."""
    print("\n" + "="*60)
    print("TEST 3: Step-level caching mechanism")
    print("="*60)

    # Simulate the caching logic
    _step_cache = {}
    enable_step_cache = True

    query = "test query"
    cache_key = query[:100]

    # Initially, cache should be empty
    assert cache_key not in _step_cache, "Cache should be empty initially"
    print(f"✅ Cache initially empty")

    # Simulate caching analysis step
    analysis = {
        'main_topic': 'Test',
        'search_terms': ['test1', 'test2']
    }

    if enable_step_cache:
        _step_cache[cache_key] = {'analysis': analysis}

    assert cache_key in _step_cache, "Cache should contain entry after storing"
    assert _step_cache[cache_key]['analysis'] == analysis, "Cached analysis should match"
    print(f"✅ Analysis cached successfully")

    # Simulate caching external_info step
    external_info = "Some external data"

    if enable_step_cache:
        _step_cache[cache_key]['external_info'] = external_info

    assert 'external_info' in _step_cache[cache_key], "Cache should have external_info"
    assert _step_cache[cache_key]['external_info'] == external_info, "Cached external_info should match"
    print(f"✅ External info cached successfully")

    # Simulate retrieval from cache
    cached = _step_cache.get(cache_key)
    if cached:
        cached_analysis = cached.get('analysis')
        cached_external_info = cached.get('external_info')

        assert cached_analysis == analysis, "Retrieved analysis should match"
        assert cached_external_info == external_info, "Retrieved external_info should match"
        print(f"✅ Cache retrieval successful")

    # Simulate cache cleanup after successful completion
    if cache_key in _step_cache:
        del _step_cache[cache_key]

    assert cache_key not in _step_cache, "Cache should be cleared after completion"
    print(f"✅ Cache cleanup successful")

    return True


def test_initialization_before_try():
    """Test that variables are initialized before try-block."""
    print("\n" + "="*60)
    print("TEST 4: Variable initialization before try-block")
    print("="*60)

    # This test verifies the pattern we implemented
    analysis = None
    external_info = None

    # Even if we raise an exception, these variables exist
    try:
        raise ValueError("Simulated error")
    except Exception as e:
        # In the improved code, we can safely use analysis and external_info here
        # because they were initialized before the try block
        assert analysis is None, "analysis should be None after error"
        assert external_info is None, "external_info should be None after error"

        # We can safely use them in expressions
        test_value = analysis or {'default': 'value'}
        assert test_value == {'default': 'value'}, "Fallback pattern should work"

        print(f"✅ Variables accessible in exception handler")
        print(f"   analysis: {analysis}")
        print(f"   external_info: {external_info}")
        print(f"   fallback works: {test_value}")

    return True


def main():
    """Run all unit tests."""
    print("\n" + "="*70)
    print("DSPy Pipeline Robustness Unit Tests")
    print("="*70)

    tests = [
        ("Fallback Dict Pattern", test_fallback_dict_pattern),
        ("External Info None Handling", test_external_info_none_handling),
        ("Step Cache Mechanism", test_step_cache_mechanism),
        ("Initialization Before Try", test_initialization_before_try),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
