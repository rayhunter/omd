"""
Test script to validate Langfuse configuration setup.
Run this to ensure Step 1 is working correctly.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import AppConfig

def test_langfuse_config():
    """Test that Langfuse configuration loads correctly."""
    
    print("🧪 Testing Langfuse Configuration...\n")
    
    try:
        # Load configuration
        config = AppConfig()
        
        # Check if langfuse config exists
        assert hasattr(config, 'langfuse'), "❌ Langfuse config not found in AppConfig"
        print("✅ Langfuse config class loaded")
        
        # Check langfuse settings
        langfuse = config.langfuse
        print(f"✅ Langfuse enabled: {langfuse.enabled}")
        print(f"✅ Langfuse host: {langfuse.host}")
        print(f"✅ Sample rate: {langfuse.sample_rate}")
        print(f"✅ Trace LLM calls: {langfuse.trace_llm_calls}")
        print(f"✅ Trace agent steps: {langfuse.trace_agent_steps}")
        print(f"✅ Trace MCP calls: {langfuse.trace_mcp_calls}")
        print(f"✅ Track costs: {langfuse.track_costs}")
        
        # Check if keys are set (without revealing them)
        if langfuse.public_key:
            print(f"✅ Public key: {langfuse.public_key[:10]}...")
        else:
            print("⚠️  Public key not set (set LANGFUSE_PUBLIC_KEY in .env)")
            
        if langfuse.secret_key:
            print(f"✅ Secret key: {langfuse.secret_key[:10]}...")
        else:
            print("⚠️  Secret key not set (set LANGFUSE_SECRET_KEY in .env)")
        
        print("\n" + "="*50)
        
        if langfuse.enabled and langfuse.public_key and langfuse.secret_key:
            print("✅ Step 1 Complete: Configuration is ready!")
            print("\nNext steps:")
            print("1. Sign up at https://cloud.langfuse.com if you haven't")
            print("2. Get your API keys from the dashboard")
            print("3. Add them to your .env file")
            return True
        elif langfuse.enabled:
            print("⚠️  Langfuse is enabled but keys are missing")
            print("\nTo complete Step 1:")
            print("1. Sign up at https://cloud.langfuse.com")
            print("2. Get your API keys from the dashboard")
            print("3. Add them to your .env file:")
            print("   LANGFUSE_PUBLIC_KEY=pk-lf-...")
            print("   LANGFUSE_SECRET_KEY=sk-lf-...")
            return False
        else:
            print("ℹ️  Langfuse is disabled in configuration")
            print("\nTo enable Langfuse:")
            print("1. Set enabled = true in config/config.development.toml")
            print("2. Add API keys to .env file")
            return False
            
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_langfuse_config()
    sys.exit(0 if success else 1)
