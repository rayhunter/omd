#!/bin/bash

# Enhanced Research Agent Streamlit Launcher
echo "🚀 Starting Enhanced Research Agent Streamlit Interface..."

# Check if we're in the right directory
if [ ! -f "enhanced_agent_streamlit.py" ]; then
    echo "❌ Error: enhanced_agent_streamlit.py not found in current directory"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check for conda environment first, then virtual environment
if [ -n "$CONDA_DEFAULT_ENV" ]; then
    echo "📦 Using conda environment: $CONDA_DEFAULT_ENV"
    # Use python from conda environment
    PYTHON_CMD="python"
elif [ -f "virtual/bin/activate" ]; then
    echo "📦 Activating virtual environment..."
    source virtual/bin/activate
    PYTHON_CMD="python"
else
    echo "⚠️  Warning: No virtual environment found"
    echo "Using system Python (make sure dependencies are installed)"
    PYTHON_CMD="python3"
fi

# Check if Streamlit is installed
if ! $PYTHON_CMD -m streamlit --version &> /dev/null; then
    echo "❌ Error: Streamlit not found"
    echo "Installing Streamlit..."
    $PYTHON_CMD -m pip install streamlit
fi

# Launch Streamlit
echo "🌐 Launching Streamlit interface..."
echo "📝 The interface will open in your default web browser"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

$PYTHON_CMD -m streamlit run enhanced_agent_streamlit.py --server.port 8501 --server.address localhost
