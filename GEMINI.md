# OMD: Enhanced Research Agent

## Project Overview

OMD (OpenManus + DSPy + MCP Integration) is an advanced AI research agent system. It combines structured reasoning (DSPy), multi-source information gathering (MCP), and browser automation (OpenManus) to provide a powerful tool for research, analysis, and decision support.

**Key Technologies:**
*   **OpenManus:** Multi-modal AI agent framework.
*   **DSPy:** Framework for programming with language models (structured reasoning).
*   **MCP (Model Control Protocol):** Standard for connecting AI assistants to data sources.
*   **Streamlit:** Web interface.
*   **Langfuse:** Observability and session tracking.
*   **Ollama:** Local LLM support.

## Building and Running

### Prerequisites
*   Python 3.11+
*   `uv` (recommended for faster package management) or `pip`.
*   Ollama (optional, for local LLM).

### Installation
The project uses a `Makefile` for convenience.

```bash
# Install all packages in development mode (requires uv)
make install

# Alternative manual installation
source virtual/bin/activate
pip install -r requirements.txt
pip install -e enhanced_agent/
pip install -e OpenManus/
```

### Configuration
1.  Copy `.env.example` to `.env`.
2.  Configure API keys (OpenAI, Langfuse, etc.) in `.env`.
3.  MCP servers are configured in `enhanced_agent/config/mcp.json`.
4.  LLM settings are in `OpenManus/config/config.toml`.

### Running the Application

**Streamlit Web Interface (Recommended):**
```bash
./run_streamlit.sh
# Access at http://localhost:8501
```

**Command Line Interface:**
```bash
python enhanced_agent/main.py
```

### Testing
```bash
make test               # Run all tests
make test-unit          # Run unit tests
make test-integration   # Run integration tests
make test-coverage      # Run tests with coverage report
```

## Development Conventions

*   **Code Style:** The project enforces formatting and linting.
    *   Format code: `make format` (uses `black`, `isort`)
    *   Lint code: `make lint` (uses `flake8`, `black --check`)
*   **Structure:**
    *   `enhanced_agent/`: The core logic for the enhanced agent capabilities.
    *   `OpenManus/`: The base agent framework.
    *   `tests/`: Comprehensive test suite (unit and integration).
    *   `docs/`: Detailed documentation for various components.
*   **Observability:** Integrates with Langfuse for tracing and session tracking.

## Key Files & Directories

*   `enhanced_agent_streamlit.py`: Main entry point for the Streamlit app.
*   `enhanced_agent/src/dspy_mcp_integration.py`: Core logic combining DSPy and MCP.
*   `OpenManus/main.py`: Entry point for the OpenManus agent.
*   `Makefile`: Automation for installation, testing, and maintenance.
*   `check_setup.py`: Script to verify the environment configuration.
