#!/usr/bin/env python3
"""
Setup checker for the Enhanced Research Agent.
Verifies all components are properly configured.
"""

import sys
import subprocess
import requests
from pathlib import Path

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (compatible)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (need 3.8+)")
        return False

def check_package(package_name, import_name=None):
    """Check if a Python package is installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} installed")
        return True
    except ImportError:
        print(f"❌ {package_name} missing - install with: pip install {package_name}")
        return False

def check_ollama():
    """Check if Ollama is running."""
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            version_info = response.json()
            print(f"✅ Ollama running (version {version_info.get('version', 'unknown')})")
            return True
        else:
            print("❌ Ollama responding but with errors")
            return False
    except requests.exceptions.RequestException:
        print("❌ Ollama not running on localhost:11434")
        print("   Start with: ollama serve")
        return False

def check_ollama_models():
    """Check if Ollama has models available."""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            models = result.stdout.strip().split('\n')[1:]  # Skip header
            if models and models[0]:
                print(f"✅ Ollama models available: {len(models)} models")
                for model in models[:3]:  # Show first 3 models
                    print(f"   - {model.split()[0]}")
                return True
            else:
                print("⚠️  Ollama running but no models installed")
                print("   Install a model with: ollama pull gemma2:2b")
                return False
        else:
            print("❌ Could not check Ollama models")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  Ollama model check timed out")
        return False
    except FileNotFoundError:
        print("⚠️  Ollama CLI not found (Ollama may still work via API)")
        return False

def check_openai_api_key():
    """Check if OpenAI API key is set."""
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        # Mask the key for security
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"✅ OpenAI API key configured: {masked_key}")
        return True
    else:
        print("⚠️  OpenAI API key not set (DSPy will use fallback mode)")
        print("   Set with: export OPENAI_API_KEY='your-key-here'")
        return False

def check_project_structure():
    """Check if project files are in place."""
    required_files = [
        "enhanced_agent/src/app.py",
        "enhanced_agent/src/dspy_modules.py", 
        "enhanced_agent/src/dspy_mcp_integration.py",
        "enhanced_agent/src/mcp_client.py",
        "enhanced_agent/config/mcp.json",
        "OpenManus/OpenManus/app/agent/base.py"
    ]
    
    all_present = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} missing")
            all_present = False
    
    return all_present

def main():
    """Run all setup checks."""
    print("🔍 Enhanced Research Agent Setup Check")
    print("=" * 45)
    
    checks = [
        ("Python Version", check_python_version),
        ("DSPy Package", lambda: check_package("dspy-ai", "dspy")),
        ("Requests Package", lambda: check_package("requests")),
        ("OpenAI Package", lambda: check_package("openai")), 
        ("Ollama Service", check_ollama),
        ("Ollama Models", check_ollama_models),
        ("OpenAI API Key", check_openai_api_key),
        ("Project Structure", check_project_structure),
    ]
    
    print("\n🔧 Checking Dependencies:")
    print("-" * 25)
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ {check_name}: Error - {e}")
            results[check_name] = False
        print()
    
    # Summary
    print("📊 Setup Summary:")
    print("-" * 18)
    
    passed = sum(results.values())
    total = len(results)
    
    for check_name, passed_check in results.items():
        status = "✅ PASS" if passed_check else "❌ FAIL"
        print(f"{check_name}: {status}")
    
    print(f"\n🏁 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! You're ready to use the enhanced research agent.")
        print("Run with: python enhanced_agent/main.py")
    elif passed >= total - 2:
        print("\n⚠️  Most checks passed. The agent should work with some limitations.")
        print("Run with: python enhanced_agent/main.py")
    else:
        print(f"\n❌ Several issues found. Please fix the failing checks before running.")
        
    print("\n💡 Quick fixes:")
    print("- Install DSPy: pip install dspy-ai>=2.0.0")  
    print("- Start Ollama: ollama serve") 
    print("- Install Ollama model: ollama pull gemma2:2b")
    print("- Set OpenAI key: export OPENAI_API_KEY='your-key'")

if __name__ == "__main__":
    main()