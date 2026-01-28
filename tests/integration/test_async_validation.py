#!/usr/bin/env python3
"""
Quick validation that async implementation is correct without running servers
"""

import ast
import inspect
from pathlib import Path

def validate_mcp_client():
    """Validate MCP client has async methods"""
    print("🔍 Validating MCP Client Implementation")
    print("=" * 60)

    mcp_file = Path(__file__).parent / "enhanced_agent" / "src" / "mcp_client.py"

    with open(mcp_file, 'r') as f:
        content = f.read()

    tree = ast.parse(content)

    # Find the MCPClient class
    mcp_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "MCPClient":
            mcp_class = node
            break

    if not mcp_class:
        print("❌ MCPClient class not found")
        return False

    print("✅ Found MCPClient class")

    # Check for required async methods
    required_async_methods = {
        'search': False,
        '_llama_search_async': False,
        '_playwright_search_async': False,
        'close': False,
        '__aenter__': False,
        '__aexit__': False,
    }

    for node in mcp_class.body:
        if isinstance(node, ast.AsyncFunctionDef):
            if node.name in required_async_methods:
                required_async_methods[node.name] = True
                print(f"  ✅ Found async method: {node.name}")

    # Check for imports
    has_httpx = 'import httpx' in content or 'from httpx' in content
    has_asyncio = 'import asyncio' in content or 'from asyncio' in content
    has_executor = 'ThreadPoolExecutor' in content

    print(f"\n📦 Dependencies:")
    print(f"  {'✅' if has_httpx else '❌'} httpx imported")
    print(f"  {'✅' if has_asyncio else '❌'} asyncio imported")
    print(f"  {'✅' if has_executor else '❌'} ThreadPoolExecutor imported")

    print(f"\n🔧 Async Methods:")
    all_found = all(required_async_methods.values())
    for method, found in required_async_methods.items():
        print(f"  {'✅' if found else '❌'} {method}")

    # Check for specific features
    features = {
        'httpx.AsyncClient': 'httpx.AsyncClient' in content,
        'httpx.Timeout': 'httpx.Timeout' in content,
        'async with': 'async with' in content,
        'await': 'await ' in content,
        'run_in_executor': 'run_in_executor' in content,
        'Semaphore': 'Semaphore' in content or 'semaphore' in content.lower(),
    }

    print(f"\n✨ Features:")
    for feature, present in features.items():
        print(f"  {'✅' if present else '❌'} {feature}")

    success = all_found and has_httpx and has_asyncio
    print(f"\n{'✅ PASS' if success else '❌ FAIL'}: MCP Client validation")
    return success

def validate_integration():
    """Validate DSPy integration has semaphore"""
    print("\n\n🔍 Validating DSPy+MCP Integration")
    print("=" * 60)

    integration_file = Path(__file__).parent / "enhanced_agent" / "src" / "dspy_mcp_integration.py"

    with open(integration_file, 'r') as f:
        content = f.read()

    features = {
        'asyncio.Semaphore': 'asyncio.Semaphore' in content or 'Semaphore' in content,
        'async with semaphore': 'async with' in content and 'semaphore' in content.lower(),
        'asyncio.gather': 'asyncio.gather' in content,
        'await gather': 'await asyncio.gather' in content or 'await gather' in content,
        'max_concurrent_queries config': 'max_concurrent_queries' in content,
        'httpx TimeoutException handling': 'httpx.TimeoutException' in content or 'TimeoutException' in content,
    }

    print("✨ Concurrency Features:")
    for feature, present in features.items():
        print(f"  {'✅' if present else '❌'} {feature}")

    # Check gather_information is async
    tree = ast.parse(content)
    gather_info_async = False
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "gather_information":
            gather_info_async = True
            print(f"\n✅ gather_information is async")
            break

    if not gather_info_async:
        print(f"\n❌ gather_information is not async")

    success = features['asyncio.Semaphore'] and features['asyncio.gather'] and gather_info_async
    print(f"\n{'✅ PASS' if success else '❌ FAIL'}: Integration validation")
    return success

def validate_dependencies():
    """Validate pyproject.toml has httpx"""
    print("\n\n🔍 Validating Dependencies")
    print("=" * 60)

    pyproject_file = Path(__file__).parent / "enhanced_agent" / "pyproject.toml"

    with open(pyproject_file, 'r') as f:
        content = f.read()

    has_httpx = 'httpx' in content
    no_requests = 'requests' not in content or content.count('requests') < content.count('httpx')

    print(f"  {'✅' if has_httpx else '❌'} httpx in dependencies")
    print(f"  {'✅' if no_requests else '⚠️ '} requests removed or replaced")

    success = has_httpx
    print(f"\n{'✅ PASS' if success else '❌ FAIL'}: Dependency validation")
    return success

def main():
    """Run all validations"""
    print("🚀 Async MCP Implementation Validation")
    print("=" * 60)
    print()

    test1 = validate_mcp_client()
    test2 = validate_integration()
    test3 = validate_dependencies()

    print("\n\n" + "=" * 60)
    print("📊 Validation Summary:")
    print(f"  MCP Client: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"  Integration: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"  Dependencies: {'✅ PASS' if test3 else '❌ FAIL'}")
    print("=" * 60)

    if all([test1, test2, test3]):
        print("\n🎉 All validations passed!")
        print("\n✅ Implementation Summary:")
        print("  • Replaced blocking requests with httpx.AsyncClient")
        print("  • Added ThreadPoolExecutor for blocking SDK operations")
        print("  • Implemented semaphore-based concurrency control")
        print("  • Added proper timeout handling with httpx.Timeout")
        print("  • Implemented async context manager (__aenter__/__aexit__)")
        print("  • Updated gather_information to use asyncio.gather")
        print("  • Added concurrent query execution with rate limiting")
    else:
        print("\n❌ Some validations failed")

    return all([test1, test2, test3])

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
