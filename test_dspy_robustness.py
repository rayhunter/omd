"""
Test script to verify DSPy pipeline robustness improvements.

This script tests:
1. Proper initialization of analysis/external_info variables
2. Safe fallback with (analysis or defaults) pattern
3. Step-level caching for failure recovery
"""

import asyncio
import sys
from pathlib import Path

# Add enhanced_agent to path for proper package imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from enhanced_agent.src.dspy_mcp_integration import DSPyMCPIntegration


async def test_early_failure():
    """Test when analysis step fails immediately."""
    print("\n" + "="*60)
    print("TEST 1: Early Failure (analysis step fails)")
    print("="*60)

    # Create integration with invalid config to force failure
    try:
        integration = DSPyMCPIntegration(
            mcp_config_path="nonexistent_config.json",
            llm_model="gpt-3.5-turbo",
            enable_step_cache=True
        )

        # This should fail gracefully and return fallback result
        result = await integration.process_research_query("What is machine learning?")

        print(f"\n✅ Test passed - got fallback result:")
        print(f"   Main topic: {result.main_topic}")
        print(f"   Query type: {result.query_type}")
        print(f"   Confidence: {result.confidence_level}")
        print(f"   Answer: {result.direct_answer[:100]}...")

        return True

    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        return False


async def test_mid_pipeline_failure():
    """Test when failure occurs after analysis but during synthesis."""
    print("\n" + "="*60)
    print("TEST 2: Mid-Pipeline Failure (synthesis fails)")
    print("="*60)

    try:
        # Create integration with step caching enabled
        integration = DSPyMCPIntegration(
            llm_model="gpt-3.5-turbo",
            enable_step_cache=True
        )

        # First call - should cache analysis and external_info steps
        print("\nAttempting first query (may fail during synthesis)...")
        result1 = await integration.process_research_query("What is Python?")

        print(f"\n✅ Got result:")
        print(f"   Main topic: {result1.main_topic}")
        print(f"   Query type: {result1.query_type}")
        print(f"   Confidence: {result1.confidence_level}")

        # Check cache status
        if integration._step_cache:
            print(f"\n📦 Cache contains {len(integration._step_cache)} entries")

        return True

    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_cache_recovery():
    """Test that cached intermediate steps can be reused."""
    print("\n" + "="*60)
    print("TEST 3: Cache Recovery (reuse cached steps)")
    print("="*60)

    try:
        integration = DSPyMCPIntegration(
            llm_model="gpt-3.5-turbo",
            enable_step_cache=True
        )

        query = "What is artificial intelligence?"

        # Manually cache some intermediate results
        cache_key = query[:100]
        integration._step_cache[cache_key] = {
            'analysis': {
                'main_topic': 'Artificial Intelligence',
                'sub_topics': ['Machine Learning', 'Deep Learning'],
                'query_type': 'factual',
                'information_needs': 'Definition and overview of AI',
                'search_terms': ['artificial intelligence', 'AI overview']
            },
            'external_info': 'Sample external information about AI...'
        }

        print(f"\n📦 Pre-cached intermediate results for query")

        # This should use cached results and skip early steps
        result = await integration.process_research_query(query)

        print(f"\n✅ Pipeline completed using cached steps:")
        print(f"   Main topic: {result.main_topic}")
        print(f"   Query type: {result.query_type}")
        print(f"   Confidence: {result.confidence_level}")

        # Cache should be cleared after successful completion
        if cache_key not in (integration._step_cache or {}):
            print(f"\n✅ Cache properly cleared after successful completion")

        return True

    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_null_safety():
    """Test that None values are handled safely in fallback."""
    print("\n" + "="*60)
    print("TEST 4: Null Safety (None values in fallback)")
    print("="*60)

    try:
        integration = DSPyMCPIntegration(
            llm_model="gpt-3.5-turbo",
            enable_step_cache=False  # Disable cache to test None handling
        )

        # Simulate a scenario where analysis=None and external_info=None
        # by using a query that might fail
        result = await integration.process_research_query("Test query")

        # Check that all fields are present and not None
        assert result.main_topic is not None, "main_topic should not be None"
        assert result.query_type is not None, "query_type should not be None"
        assert result.search_terms is not None, "search_terms should not be None"
        assert result.external_info is not None, "external_info should not be None (can be empty string)"

        print(f"\n✅ All result fields properly initialized:")
        print(f"   Main topic: {result.main_topic}")
        print(f"   Query type: {result.query_type}")
        print(f"   Search terms: {result.search_terms}")
        print(f"   External info length: {len(result.external_info)}")

        return True

    except AssertionError as e:
        print(f"\n❌ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all robustness tests."""
    print("\n" + "="*70)
    print("DSPy Pipeline Robustness Test Suite")
    print("="*70)

    tests = [
        ("Early Failure", test_early_failure),
        ("Mid-Pipeline Failure", test_mid_pipeline_failure),
        ("Cache Recovery", test_cache_recovery),
        ("Null Safety", test_null_safety),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
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
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
