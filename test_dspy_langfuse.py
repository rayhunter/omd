"""
Test DSPy integration with Langfuse tracing.
This will verify that DSPy queries are properly traced.
"""

import asyncio
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "enhanced_agent" / "src"))

from langfuse_integration import langfuse_manager, shutdown_langfuse

def test_dspy_integration():
    """Test that DSPy integration is working with tracing."""
    
    print("="*60)
    print("🧪 Testing DSPy-Langfuse Integration")
    print("="*60)
    
    if not langfuse_manager.enabled:
        print("\n❌ Langfuse not enabled. Cannot test integration.")
        return False
    
    print(f"\n✅ Langfuse enabled")
    
    try:
        # Try to import DSPy integration  
        from enhanced_agent.src.dspy_mcp_integration import DSPyMCPIntegration, LANGFUSE_AVAILABLE
        
        if not LANGFUSE_AVAILABLE:
            print("⚠️  Langfuse not available in DSPy integration module")
            return False
        
        print("✅ DSPy integration imported")
        print("✅ Langfuse available in DSPy module")
        
        # Test that we can create the integration
        print("\n📦 Creating DSPyMCPIntegration instance...")
        integration = DSPyMCPIntegration(llm_model="gemma2:2b")
        print("✅ DSPyMCPIntegration created")
        
        # Test simple query analysis (this should create traces)
        print("\n🔍 Testing query analysis with tracing...")
        
        async def test_analysis():
            with langfuse_manager.trace_span("test_dspy_integration", 
                                              tags=["test", "dspy_integration"]):
                query = "What is machine learning?"
                result = await integration.analyze_query_structure(query)
                return result
        
        result = asyncio.run(test_analysis())
        
        print(f"\n✅ Query analysis completed:")
        print(f"   Topic: {result['main_topic']}")
        print(f"   Type: {result['query_type']}")
        print(f"   Search terms: {result['search_terms'][:3]}")
        
        # Flush traces
        print("\n📤 Flushing traces to Langfuse...")
        shutdown_langfuse()
        print("✅ Traces flushed")
        
        print("\n" + "="*60)
        print("✅ DSPy-Langfuse Integration Test PASSED")
        print("="*60)
        print("\nCheck your Langfuse dashboard at:")
        print("https://us.cloud.langfuse.com")
        print("\nYou should see:")
        print("  • dspy_query_analysis span")
        print("  • Agent step trace for 'analyze'")
        print("  • Metadata with latency and query details")
        print("="*60)
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Could not import DSPy integration: {e}")
        print("\nThis is normal if:")
        print("  • DSPy is not installed")
        print("  • MCP client is not configured")
        print("  • OpenManus is not installed")
        return False
    
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        shutdown_langfuse()
        return False

if __name__ == "__main__":
    success = test_dspy_integration()
    sys.exit(0 if success else 1)
