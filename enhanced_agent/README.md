# Enhanced Research Agent

A powerful research agent that combines DSPy's structured reasoning with MCP (Model Control Protocol) for enhanced information gathering and response generation. Integrated with OpenManus framework for comprehensive AI agent capabilities.

## Features

- **DSPy Integration**: Structured reasoning with GPT models for query analysis and response generation
- **MCP Multi-Server Support**: Real-time information gathering from multiple sources (Ollama, web search, Wikipedia, arXiv, etc.)
- **Streamlit Web Interface**: User-friendly web interface with progress tracking and download capabilities
- **OpenManus Integration**: Seamless integration as a specialized tool within the OpenManus framework
- **Environment Variable Support**: Automatic .env file loading for API keys and configuration
- **Async/Await Architecture**: Efficient processing with proper error handling and graceful degradation
- **Comprehensive Testing**: Full test suite with unit and integration tests

## Prerequisites

- **Python 3.11-3.13** (Python 3.13.5 supported with warnings)
- **Ollama** running on port 11434 (for local LLM server)
- **OpenAI API Key** (for DSPy structured reasoning)
- **Virtual Environment**: Project uses `virtual/` venv
- **OpenManus Framework** (integrated as part of the OMD project)

## Installation

### Quick Setup (Recommended)
From the project root directory:
```bash
# Install all dependencies and packages
make install

# Set up environment variables
python setup_env.py

# Start the web interface
./run_streamlit.sh
```

### Manual Setup
1. **Set up virtual environment** (if not already done):
```bash
# From project root
cd /path/to/omd
source virtual/bin/activate
```

2. **Install enhanced_agent dependencies**:
```bash
cd enhanced_agent
./virtual/bin/pip install -r requirements.txt
./virtual/bin/pip install -e .
```

3. **Configure environment variables**:
```bash
# Create/edit .env file in project root
OPENAI_API_KEY=your_openai_api_key_here
```

4. **Configure MCP servers** (optional):
- Edit `config/mcp.json` or `config/mcp_extended.json`
- Default configuration uses Ollama with gemma2:2b model
- Multiple servers available: web-search, wikipedia, arxiv, finance, etc.

## Usage

Run the agent from the enhanced_agent directory:
```bash
python main.py
```

Enter your research queries when prompted. Type 'quit' or 'exit' to stop the agent.

## Configuration

### Environment Variables (.env file in project root)
```bash
# Required for DSPy structured reasoning
OPENAI_API_KEY=your_openai_api_key_here

# Optional for additional MCP servers
NEWS_API_KEY=your_news_api_key_here
WEATHER_API_KEY=your_weather_api_key_here
GITHUB_TOKEN=your_github_token_here
```

### MCP Configuration (config/mcp.json)
```json
{
    "servers": {
        "llama-mcp": {
            "url": "http://localhost:11434",
            "model": "gemma2:2b",
            "context_length": 4096,
            "temperature": 0.7,
            "max_tokens": 1024
        }
    },
    "default_server": "llama-mcp"
}
```

### Extended MCP Configuration (config/mcp_extended.json)
Supports multiple information sources:
- **llama-mcp**: Local Ollama server
- **web-search**: DuckDuckGo search
- **wikipedia**: Wikipedia API
- **arxiv**: Academic papers
- **finance**: Yahoo Finance
- **news-api**: News headlines (requires API key)
- **weather**: Weather data (requires API key)

## Architecture

The enhanced agent follows a sophisticated multi-step process:

1. **Query Analysis**: DSPy structured reasoning analyzes the user query
2. **Information Gathering**: Multiple MCP servers gather relevant information  
3. **Structured Processing**: DSPy pipeline processes and synthesizes information
4. **Response Generation**: Coherent, well-structured response with citations

### Key Components
- **DSPy Integration** (`src/dspy_mcp_integration.py`): Structured reasoning pipeline
- **MCP Client** (`src/mcp_client.py` & `src/enhanced_mcp_client.py`): Multi-server information gathering
- **OpenManus Integration** (`../OpenManus/app/tool/enhanced_agent_tool.py`): Tool integration
- **Streamlit Interface** (`../enhanced_agent_streamlit.py`): Web UI

## Testing

The project includes comprehensive testing:
- **Unit Tests**: Individual component testing (`tests/unit/`)
- **Integration Tests**: Full system testing (`tests/integration/`)
- **Async Support**: Full async/await testing with pytest-asyncio
- **Mocking**: Proper mocking of external services (OpenAI, MCP servers)

## Troubleshooting

### Common Issues
1. **OpenAI API Errors**: Ensure `OPENAI_API_KEY` is set in `.env` file
2. **MCP Connection Issues**: Verify Ollama is running on port 11434
3. **Import Errors**: Ensure virtual environment is activated and packages installed
4. **Streamlit Errors**: Check for syntax errors and form/button placement

### Virtual Environment
The project uses `virtual/` directory for the virtual environment:
```bash
# Activate virtual environment
source virtual/bin/activate

# Install dependencies
./virtual/bin/pip install -r requirements.txt
```

## License

Same as OpenManus framework 