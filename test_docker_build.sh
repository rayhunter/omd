#!/bin/bash
set -e

echo "========================================="
echo "Testing Docker Build Process"
echo "========================================="
echo ""

# Build a test Docker image
echo "Building test Docker image..."
docker build -t omd-test:latest -f- . <<'EOF'
FROM python:3.12-slim

WORKDIR /app

# Install git (needed for some dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# Copy requirements and OpenManus
COPY requirements.txt .
COPY OpenManus OpenManus/

# Test: Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Test: Install OpenManus
RUN pip install --no-cache-dir OpenManus/

# Test: Verify imports work
RUN python -c "from openmanus.agent import ReActAgent; from openmanus.config import Config; from openmanus.schema import Message; print('✓ OpenManus imports successful')"

# Test: Check package is installed
RUN pip show openmanus

CMD ["echo", "Build test successful"]
EOF

echo ""
echo "========================================="
echo "Docker build test PASSED! ✓"
echo "========================================="
echo ""
echo "The build will work on Railway."
echo ""
echo "Cleaning up test image..."
docker rmi omd-test:latest

echo "Done!"
