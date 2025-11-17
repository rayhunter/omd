#!/usr/bin/env python3
"""
Test script to verify package installations and imports work correctly.
Run this after installing packages with: pip install -e OpenManus && pip install -e enhanced_agent
"""

import sys

def test_openmanus_imports():
    """Test that OpenManus package imports correctly."""
    print("🧪 Testing OpenManus imports...")

    try:
        # Test basic imports
        from openmanus import Manus, BaseAgent, ReActAgent, ToolCallAgent
        print("  ✅ Main agent classes imported successfully")

        from openmanus.config import Config
        print("  ✅ Config imported successfully")

        from openmanus.tool import BaseTool
        print("  ✅ Tool base class imported successfully")

        from openmanus.agent.manus import Manus as DirectManus
        print("  ✅ Direct agent import works")

        from openmanus.logger import logger
        print("  ✅ Logger imported successfully")

        # Check version
        from openmanus import __version__
        print(f"  ℹ️  OpenManus version: {__version__}")

        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False


def test_enhanced_agent_imports():
    """Test that enhanced_agent package imports correctly."""
    print("\n🧪 Testing enhanced_agent imports...")

    try:
        # Test basic imports
        from enhanced_agent.src.app import run_enhanced_agent, create_agent
        print("  ✅ Main app functions imported successfully")

        from enhanced_agent.src.dspy_mcp_integration import DSPyMCPIntegration
        print("  ✅ DSPy MCP integration imported successfully")

        from enhanced_agent.src.mcp_client import MCPClient
        print("  ✅ MCP client imported successfully")

        from enhanced_agent.src.dspy_modules import QuickAnalysis
        print("  ✅ DSPy modules imported successfully")

        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        print("  💡 Make sure both packages are installed:")
        print("     pip install -e OpenManus")
        print("     pip install -e enhanced_agent")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False


def test_dependency_chain():
    """Test that enhanced_agent can use OpenManus components."""
    print("\n🧪 Testing dependency chain (enhanced_agent -> openmanus)...")

    try:
        # This should work because enhanced_agent depends on openmanus
        from enhanced_agent.src.app import ReActAgent, Config
        print("  ✅ Enhanced agent can import OpenManus components")

        # Test that they're the same as direct imports
        from openmanus.agent import ReActAgent as DirectReActAgent
        from openmanus.config import Config as DirectConfig

        if ReActAgent is DirectReActAgent:
            print("  ✅ Imports reference the same classes (no duplication)")
        else:
            print("  ⚠️  Warning: Imports don't reference the same classes")

        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False


def test_no_sys_path_pollution():
    """Verify that sys.path doesn't contain project-specific paths."""
    print("\n🧪 Testing for sys.path pollution...")

    import os
    project_root = os.path.dirname(os.path.abspath(__file__))

    polluted = False
    for path in sys.path:
        # Check for project-specific paths that shouldn't be there after proper installation
        if "enhanced_agent/src" in path or "/OpenManus/app" in path:
            print(f"  ⚠️  Found project-specific path in sys.path: {path}")
            polluted = True

    if not polluted:
        print("  ✅ No project-specific paths in sys.path (clean installation)")
        return True
    else:
        print("  ❌ sys.path contains project-specific paths (possible manual manipulation)")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("📦 Package Installation and Import Test Suite")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("OpenManus imports", test_openmanus_imports()))
    results.append(("Enhanced agent imports", test_enhanced_agent_imports()))
    results.append(("Dependency chain", test_dependency_chain()))
    results.append(("No sys.path pollution", test_no_sys_path_pollution()))

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Package installation is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please ensure packages are installed correctly:")
        print("   pip install -e OpenManus")
        print("   pip install -e enhanced_agent")
        return 1


if __name__ == "__main__":
    sys.exit(main())
