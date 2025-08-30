#!/usr/bin/env python3
"""
Test runner script for the OMD project.

This script provides convenient commands to run different types of tests.
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle the output."""
    print(f"\n🚀 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
        else:
            print(f"❌ {description} failed with return code {result.returncode}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="OMD Project Test Runner")
    parser.add_argument(
        "test_type", 
        nargs="?", 
        default="all",
        choices=["all", "unit", "integration", "fast", "slow"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Run tests with coverage reporting"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true", 
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Change to project root
    project_root = Path(__file__).parent
    import os
    os.chdir(project_root)
    
    print("🧪 OMD Project Test Runner")
    print(f"📂 Working directory: {project_root}")
    
    # Build pytest command using virtual environment
    pytest_cmd = "./virtual/bin/python -m pytest"
    
    if args.verbose:
        pytest_cmd += " -v"
    
    if args.coverage:
        pytest_cmd += " --cov=enhanced_agent --cov=OpenManus --cov-report=html --cov-report=term"
    
    # Add test type specific options
    if args.test_type == "unit":
        pytest_cmd += " -m unit"
    elif args.test_type == "integration":
        pytest_cmd += " -m integration"
    elif args.test_type == "fast":
        pytest_cmd += " -m 'not slow'"
    elif args.test_type == "slow":
        pytest_cmd += " -m slow"
    elif args.test_type == "all":
        pytest_cmd += " tests/"
    
    # Run the tests
    success = run_command(pytest_cmd, f"Running {args.test_type} tests")
    
    if success:
        print("\n🎉 All tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
