# Enhanced Research Agent

A powerful research agent that combines DSPy's structured reasoning with MCP (Model Control Protocol) for enhanced information gathering and response generation.

## Features

- DSPy integration for structured reasoning
- MCP support for real-time information gathering
- ReAct pattern for step-by-step processing
- Configurable LLM backends
- Async/await pattern for efficient processing

## Prerequisites

- Python 3.8+
- Ollama running on port 11434 (for llama-mcp server)
- OpenManus framework

## Installation

1. Clone the repository and navigate to the enhanced_agent directory:
```bash
cd enhanced_agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package in development mode:
```bash
pip install -e .
```

4. Configure MCP:
- Edit `config/mcp.json` to set up your preferred MCP servers
- Default configuration uses Ollama with llama2 model

## Usage

Run the agent from the enhanced_agent directory:
```bash
python main.py
```

Enter your research queries when prompted. Type 'quit' or 'exit' to stop the agent.

## Configuration

### MCP Configuration (config/mcp.json)
```json
{
    "servers": {
        "llama-mcp": {
            "url": "http://localhost:11434",
            "model": "gemma3",
            "context_length": 4096,
            "temperature": 0.7,
            "max_tokens": 2048
        }
    },
    "default_server": "llama-mcp"
}
```

## Architecture

The agent uses a three-step process:
1. Query structuring using DSPy
2. Information gathering via MCP
3. Response generation with context integration

## License

Same as OpenManus framework 