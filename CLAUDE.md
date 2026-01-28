# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OMD (OpenManus + DSPy) is an enhanced AI research agent that combines three powerful technologies:
- **OpenManus**: Multi-modal AI agent framework with browser automation and tool integration
- **DSPy**: Structured reasoning and prompt optimization for intelligent query analysis
- **MCP (Model Control Protocol)**: Multi-server information gathering from diverse sources

The system provides CLI, web (Streamlit), and programmatic interfaces for AI-powered research, analysis, and decision support.

## Repository Structure

This is a monorepo containing two Python packages:
- `OpenManus/` - General-purpose AI agent framework (dependency)
- `enhanced_agent/` - Enhanced research agent with DSPy+MCP integration (depends on OpenManus)

Both are installable packages with `pyproject.toml`. Tests are consolidated at the repository root in `tests/`.

## Core Commands

### Installation & Setup
```bash
# Full development setup (recommended)
make install

# Manual setup (install in order - enhanced_agent depends on OpenManus)
pip install -e OpenManus
pip install -e enhanced_agent

# Configuration
cp .env.example .env                                                    # Configure environment variables
cp OpenManus/config/config.example.toml OpenManus/config/config.toml  # Configure LLM providers
# Edit config.toml with your API keys (OpenAI, Anthropic, Azure, or Ollama)
```

### Running the Application
```bash
# Streamlit web interface (recommended for interactive use)
./run_streamlit.sh

# Command-line interface
python enhanced_agent/main.py

# OpenManus standalone
python OpenManus/run_flow.py
```

### Testing
```bash
# Run all tests
make test

# Run specific test categories
make test-unit              # Unit tests only
make test-integration       # Integration tests only
make test-fast             # Fast tests (exclude slow)

# Direct pytest usage (from repository root)
pytest tests/              # All tests
pytest -m unit             # Unit tests only
pytest -m integration      # Integration tests only
pytest -m "not slow"       # Exclude slow tests

# With coverage
make test-coverage
```

### Code Quality
```bash
make format    # Auto-format code (black + isort)
make lint      # Check code style (black + flake8 + isort)
make clean     # Clean build artifacts and caches
```

### Individual Test Files
```bash
# Run a single test file
pytest tests/unit/test_dspy_robustness.py -v

# Run specific test function
pytest tests/integration/test_async_mcp.py::test_function_name -v
```

## Architecture

### Integration Pipeline Flow

```
User Query
    ↓
DSPy Query Analysis (dspy_modules.py)
    - Extract topics and search terms
    - Classify query type (factual/analytical/creative)
    - Generate optimized search queries
    ↓
MCP Multi-Server Routing (unified_mcp_client.py)
    - Route to appropriate servers based on query type
    - Parallel queries to multiple sources
    - Aggregate and deduplicate results
    ↓
OpenManus ReAct Agent (app.py)
    - Step-by-step reasoning
    - Tool execution (browser automation, file ops, etc.)
    - State management
    ↓
Structured Response Generation
    - Direct answer
    - Key insights
    - Supporting information
    - Actionable next steps
```

### Key Components

**DSPy Integration (`enhanced_agent/src/`)**
- `dspy_modules.py` - DSPy signatures and modules for structured reasoning
  - `QueryAnalysis`: Extracts topics, query types, and search terms
  - `InformationSynthesis`: Combines external info with query context
  - `ResponseGeneration`: Produces structured answers
  - `StructuredResearchPipeline`: Complete research workflow orchestration
- `dspy_mcp_integration.py` - Orchestrates DSPy reasoning with MCP information gathering
- Works with or without OpenAI API key (uses local models when unavailable)

**MCP Client (`enhanced_agent/src/`)**
- `unified_mcp_client.py` - Multi-server MCP client with intelligent routing
- `mcp_config.py` - Configuration management for MCP servers
- Supports: Ollama, DuckDuckGo web search, Wikidata, DBpedia, arXiv, news, weather
- DSPy-driven server selection based on query analysis
- Configured via `enhanced_agent/config/mcp.json`

**OpenManus Framework (`OpenManus/app/`)**
- `agent/` - Agent implementations (BaseAgent, ReActAgent, ToolCallAgent, Manus)
- `tool/` - Tool framework with browser automation (browser-use), file ops, search, terminal
- `flow/` - Workflow orchestration with planning and execution flows
- `sandbox/` - Docker-based isolated execution environment
- `config.py` - Configuration singleton (auto-loads from config.toml)

**Streamlit Interface**
- `enhanced_agent_streamlit.py` - Web UI with session management
- `run_streamlit.sh` - Launcher script with automatic venv activation
- Integrates Langfuse session tracking when configured

### State Management

**Agent States**: IDLE → RUNNING → FINISHED/ERROR
- Proper async/await for all operations
- Timeout handling with `asyncio.wait_for()`
- Context managers for resource cleanup

**Session Isolation** (when Langfuse enabled):
- Session-scoped conversation history
- User attribution and tracking
- Session grouping in observability platform

## Configuration

### LLM Provider Configuration (`OpenManus/config/config.toml`)

Supports multiple providers. Example for Anthropic Claude:

```toml
[llm]
model = "claude-3-7-sonnet-20250219"
base_url = "https://api.anthropic.com/v1/"
api_key = "YOUR_API_KEY"
max_tokens = 8192
temperature = 0.0
```

Other supported providers: OpenAI, Azure OpenAI, Ollama (local)

### MCP Server Configuration (`enhanced_agent/config/mcp.json`)

Configure information sources and routing rules. Key servers:
- `web-search`: DuckDuckGo for current events and real-time data
- `wikidata`: Structured knowledge base with verified facts
- `dbpedia`: Structured Wikipedia data (850M+ semantic triples)
- `arxiv`: Scientific papers and research
- `news-api`: Breaking news and current events
- `weather`: Weather forecasts
- `llama-mcp`: Local Ollama model for general reasoning

The `routing_rules` section maps query types to appropriate servers using DSPy-driven selection.

### Environment Variables (`.env`)

```bash
# Optional: Enhanced DSPy performance
OPENAI_API_KEY=your_key

# Optional: Observability (Langfuse)
LANGFUSE_PUBLIC_KEY=your_key
LANGFUSE_SECRET_KEY=your_key
LANGFUSE_HOST=https://cloud.langfuse.com

# Optional: Additional MCP servers
NEWS_API_KEY=your_key
WEATHER_API_KEY=your_key
```

## Development Patterns

### Package Structure
- Both packages use `pyproject.toml` for metadata and dependencies
- Install with `-e` flag for editable mode during development
- No `sys.path` manipulation needed after proper installation
- Import pattern: `from openmanus import Manus` or `from enhanced_agent.src.app import run_enhanced_agent`

### Async/Await Architecture
- All agents and tools are async
- Use `asyncio.wait_for()` for timeout handling
- Context managers for proper resource cleanup
- Event loop reuse handled by framework

### Error Handling
- State-based error recovery in agents
- Graceful degradation (DSPy optional, Langfuse optional)
- Duplicate detection and stuck state handling
- Proper logging with privacy-aware redaction when enabled

### Testing Structure
- Consolidated test directory at repository root: `tests/`
- Test categories: `unit/` and `integration/`
- Pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- Async test support via `pytest-asyncio`
- Shared fixtures in `tests/conftest.py`

## Important Implementation Details

### MCP Server Selection
The system uses DSPy to intelligently route queries to appropriate MCP servers:
- Query analysis extracts topics and intent
- Routing rules map query types to server capabilities
- Multiple servers can be queried in parallel
- Results are aggregated and deduplicated

### Langfuse Integration
Optional observability layer for production monitoring:
- Session-based conversation tracking
- User attribution
- Performance metrics and token usage
- Cost tracking
- Enabled when environment variables are set
- Code gracefully degrades when unavailable

### Browser Automation
OpenManus integrates `browser-use` for web interaction:
- Playwright-based browser control
- Screenshot capture
- Form filling and navigation
- Tool integration via `OpenManus/app/tool/browser_use_tool.py`

### Privacy Features
Optional privacy layer for sensitive data:
- Redacted logging via `privacy.py`
- Session management with data isolation
- Import gracefully fails when not available

## Prerequisites

**Required**:
- Python 3.11-3.13 (3.12 recommended)
- Virtual environment (conda or venv)

**For Full Functionality**:
- Ollama running on port 11434 (for MCP local model)
- LLM provider API key in `config.toml` (OpenAI, Anthropic, etc.)
- Docker (for OpenManus sandbox features)

**Optional**:
- OpenAI API key for enhanced DSPy performance
- Langfuse account for observability
- News API and Weather API keys for additional MCP servers

## Common Development Workflows

### Adding a New MCP Server
1. Add server configuration to `enhanced_agent/config/mcp.json`
2. Update routing rules to include new server capabilities
3. Implement server-specific logic in `unified_mcp_client.py` if needed
4. Add integration tests in `tests/integration/`

### Modifying DSPy Pipeline
1. Edit DSPy signatures in `enhanced_agent/src/dspy_modules.py`
2. Update `StructuredResearchPipeline` orchestration
3. Test with `pytest tests/unit/test_dspy_robustness.py`
4. Verify integration with `pytest tests/integration/test_async_mcp.py`

### Adding New OpenManus Tools
1. Create tool in `OpenManus/app/tool/`
2. Inherit from `BaseTool` and implement `async def execute()`
3. Register in tool collection
4. Add unit tests in `tests/unit/`

### Testing Changes
```bash
# Quick validation during development
make format && make test-fast

# Full test suite before commit
make format && make lint && make test

# Test specific component
pytest tests/unit/test_dspy_robustness.py -v -s
```

## Build System Notes

- Uses UV package manager for fast dependency resolution
- Makefile coordinates multi-package builds
- Lock files can be generated with `make lock`
- Virtual environment at `virtual/` (not `.venv/`)
- Each package has separate dependencies in `pyproject.toml`
- Consolidated test runner uses `./virtual/bin/python`
