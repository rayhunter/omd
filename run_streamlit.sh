#!/bin/bash

# Enhanced Research Agent Streamlit Launcher
echo "🚀 Starting Enhanced Research Agent Streamlit Interface..."

# Check if we're in the right directory
if [ ! -f "enhanced_agent_streamlit.py" ]; then
    echo "❌ Error: enhanced_agent_streamlit.py not found in current directory"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Activate virtual environment
if [ -f "virtual/bin/activate" ]; then
    echo "📦 Activating virtual environment..."
    source virtual/bin/activate
else
    echo "❌ Error: Virtual environment not found at 'virtual/bin/activate'"
    echo "Please ensure the virtual environment is set up correctly"
    exit 1
fi

# Check if Streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Error: Streamlit not found in virtual environment"
    echo "Installing Streamlit..."
    export PATH="$HOME/.local/bin:$PATH"
    uv pip install streamlit
fi

# Launch Streamlit
echo "🌐 Launching Streamlit interface..."
echo "📝 The interface will open in your default web browser"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

streamlit run enhanced_agent_streamlit.py --server.port 8501 --server.address localhost
