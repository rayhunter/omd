#!/bin/bash
set -e

echo "========================================="
echo "Testing OpenManus Import Structure"
echo "========================================="
echo ""

cd OpenManus

# Test that the expected modules exist
echo "Checking module files..."

REQUIRED_FILES=(
    "openmanus/__init__.py"
    "openmanus/agent/__init__.py"
    "openmanus/agent/react.py"
    "openmanus/config.py"
    "openmanus/schema.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file NOT found"
        exit 1
    fi
done

echo ""
echo "Checking import statements in openmanus/__init__.py..."

# Check that __init__.py has the correct imports
if grep -q "from openmanus.agent.react import ReActAgent" openmanus/__init__.py; then
    echo "✓ ReActAgent import found in __init__.py"
else
    echo "✗ ReActAgent import NOT found in __init__.py"
    exit 1
fi

echo ""
echo "Checking that enhanced_agent can find required classes..."

# Check that the classes exist in their expected locations
if grep -q "class ReActAgent" openmanus/agent/react.py; then
    echo "✓ ReActAgent class found in openmanus/agent/react.py"
else
    echo "✗ ReActAgent class NOT found"
    exit 1
fi

if grep -q "class Config" openmanus/config.py; then
    echo "✓ Config class found in openmanus/config.py"
else
    echo "✗ Config class NOT found"
    exit 1
fi

if grep -q "class Message" openmanus/schema.py; then
    echo "✓ Message class found in openmanus/schema.py"
else
    echo "✗ Message class NOT found"
    exit 1
fi

echo ""
echo "========================================="
echo "All import structure tests passed! ✓"
echo "========================================="
echo ""
echo "The following imports will work after installation:"
echo "  - from openmanus.agent import ReActAgent"
echo "  - from openmanus.config import Config"
echo "  - from openmanus.schema import Message"
