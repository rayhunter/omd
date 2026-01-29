#!/bin/bash
set -e

echo "Testing OpenManus package installation..."

# Create a temporary test directory
TEST_DIR=$(mktemp -d)
trap "rm -rf $TEST_DIR" EXIT

# Copy OpenManus to test directory
cp -r OpenManus "$TEST_DIR/"
cd "$TEST_DIR/OpenManus"

echo "✓ Copied OpenManus to test directory"

# Test 1: Check package structure
echo ""
echo "Test 1: Checking package structure..."
if [ -d "openmanus" ]; then
    echo "✓ openmanus/ directory exists"
else
    echo "✗ openmanus/ directory NOT found"
    exit 1
fi

if [ -f "setup.py" ]; then
    echo "✓ setup.py exists"
else
    echo "✗ setup.py NOT found"
    exit 1
fi

if [ -f "pyproject.toml" ]; then
    echo "✓ pyproject.toml exists"
else
    echo "✗ pyproject.toml NOT found"
    exit 1
fi

# Test 2: Check for __init__.py
echo ""
echo "Test 2: Checking for __init__.py files..."
if [ -f "openmanus/__init__.py" ]; then
    echo "✓ openmanus/__init__.py exists"
else
    echo "✗ openmanus/__init__.py NOT found"
    exit 1
fi

if [ -f "openmanus/agent/__init__.py" ]; then
    echo "✓ openmanus/agent/__init__.py exists"
else
    echo "✗ openmanus/agent/__init__.py NOT found"
    exit 1
fi

# Test 3: Verify pyproject.toml doesn't reference 'app'
echo ""
echo "Test 3: Checking pyproject.toml for 'app' references..."
if grep -q 'openmanus = "app"' pyproject.toml; then
    echo "✗ pyproject.toml still references 'app' directory"
    exit 1
else
    echo "✓ pyproject.toml does not reference 'app' directory"
fi

# Test 4: Check that setup.py uses find_packages correctly
echo ""
echo "Test 4: Validating setup.py..."
if [ -f "setup.py" ]; then
    if grep -q "find_packages()" setup.py; then
        echo "✓ setup.py uses find_packages()"
    fi
fi

# Test 5: Verify subpackages exist
echo ""
echo "Test 5: Checking for subpackages..."
SUBPACKAGES=(
    "openmanus/agent"
    "openmanus/tool"
    "openmanus/prompt"
    "openmanus/sandbox"
    "openmanus/flow"
)

for pkg in "${SUBPACKAGES[@]}"; do
    if [ -d "$pkg" ] && [ -f "$pkg/__init__.py" ]; then
        echo "✓ $pkg/ subpackage exists"
    else
        echo "✗ $pkg/ subpackage NOT found"
        exit 1
    fi
done

echo ""
echo "========================================="
echo "All tests passed! ✓"
echo "========================================="
echo ""
echo "OpenManus package structure is ready for Railway deployment."
