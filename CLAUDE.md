# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This workspace contains multiple AI/ML development projects focused on agent-based automation, research, and web interaction. The repository combines OpenManus (a general-purpose AI agent framework) with enhanced research capabilities through DSPy and MCP integration.

## Key Projects

### OpenManus (General AI Agent Framework)
- **Location**: `OpenManus/`
- **Type**: Python-based multi-modal AI agent system with browser automation and tool integration
- **Primary Entry Points**:
  - `python OpenManus/main.py` - Basic agent with terminal input
  - `python OpenManus/run_flow.py` - Advanced planning flows with timeout handling (recommended)
- **Configuration**: Copy `OpenManus/config/config.example.toml` to `OpenManus/config/config.toml` and configure LLM API keys
- **Testing**: `pytest OpenManus/tests/` (supports async tests with pytest-asyncio)
- **Architecture**: Agent-based with tool collection, browser automation via browser-use, sandbox support

### Enhanced MCP Agent with DSPy Integration
- **Location**: `enhanced_agent/` (complete package with DSPy modules)
- **Type**: Research agent combining OpenManus ReAct + DSPy structured reasoning + MCP integration
- **Primary Entry Points**:
  - `python enhanced_agent/main.py` - Full integration with DSPy+MCP+OpenManus
  - `python enhanced_agent/src/app.py` - Alternative entry point
  - `./run_streamlit.sh` - Streamlit web interface (recommended for interactive use)
- **Dependencies**: 
  - `dspy-ai>=2.0.0` - Structured reasoning and prompt optimization
  - OpenManus ReAct agent framework
  - MCP client for external information gathering

## Development Commands

### Build System (Using Makefile and UV)
The repository uses a unified build system with both Makefile and shell scripts:

#### Core Commands
- `make install` - Install all packages in development mode using uv
- `make test` - Run all tests across projects (uses pytest with async support)
- `make test-unit` - Run unit tests only
- `make test-integration` - Run integration tests only  
- `make test-coverage` - Run tests with coverage reporting
- `make lint` - Run linting (black, flake8, isort)
- `make format` - Auto-format code (black, isort)
- `make clean` - Clean up virtual environments and cache files

#### Development Scripts
- `./scripts/dev.sh setup` - Set up complete development environment
- `./scripts/dev.sh run [module]` - Run specific modules
- `./run_streamlit.sh` - Launch Streamlit interface for enhanced agent

### Individual Project Commands

#### OpenManus Agent Development
1. **Installation**:
   ```bash
   # Install as an editable package (recommended for development)
   pip install -e OpenManus
   # Or with optional dependencies
   pip install -e "OpenManus[dev,dspy]"
   ```

2. **Setup**:
   ```bash
   cp OpenManus/config/config.example.toml OpenManus/config/config.toml
   # Edit config.toml with your LLM API keys
   ```

3. **Running**:
   ```bash
   python OpenManus/main.py          # Basic agent
   openmanus                         # Using installed command
   python OpenManus/run_flow.py      # Planning flows with timeout (recommended)
   ```

4. **Testing**:
   ```bash
   pytest OpenManus/tests/           # All OpenManus tests
   pytest -m "not slow"              # Fast tests only
   ```

5. **Importing in Code**:
   ```python
   from openmanus import Manus, ReActAgent
   from openmanus.config import Config
   from openmanus.tool import BaseTool
   ```

#### Enhanced Agent with DSPy+MCP Integration
1. **Installation**:
   ```bash
   # Install OpenManus first (required dependency)
   pip install -e OpenManus

   # Install enhanced_agent as an editable package
   pip install -e enhanced_agent
   # Or with optional dependencies
   pip install -e "enhanced_agent[dev]"
   ```

2. **Configuration**:
   ```bash
   # Configure MCP servers in enhanced_agent/config/mcp.json
   # Requires Ollama on port 11434 for default setup
   export OPENAI_API_KEY="your_key"  # Optional, for DSPy structured reasoning
   ```

3. **Running**:
   ```bash
   python enhanced_agent/main.py     # Full integration
   ./run_streamlit.sh                # Web interface (recommended)
   python test_dspy_standalone.py    # Test components independently
   ```

4. **Importing in Code**:
   ```python
   from enhanced_agent.src.app import run_enhanced_agent, create_agent
   from enhanced_agent.src.dspy_mcp_integration import DSPyMCPIntegration
   from enhanced_agent.src.mcp_client import MCPClient
   ```

## Architecture Overview

### OpenManus Core Architecture
The OpenManus framework follows a modular, plugin-based architecture:

#### Agent System (`OpenManus/app/agent/`)
- **BaseAgent** (`base.py`): Abstract base with state management, memory, and execution loop
- **Agent Patterns**: 
  - `ToolCallAgent` - Direct tool calling with structured outputs
  - `ReActAgent` - Reasoning and Acting pattern for step-by-step problem solving
  - `Manus` - Main implementation combining multiple agent capabilities
  - `PlanningAgent` - Strategic planning with structured flows
- **State Management**: Agents transition through IDLE → RUNNING → FINISHED/ERROR states
- **Memory System**: Message-based conversation memory with role-based message handling

#### Tool Framework (`OpenManus/app/tool/`)
- **BaseTool** (`base.py`): Abstract base class with standardized execute interface
- **Built-in Tools**: File operations, web search, Python execution, terminal access, browser automation
- **Tool Results**: Structured return format with output, errors, images, and system messages
- **Tool Collections**: Organized groupings of related tools for specific domains

#### Flow System (`OpenManus/app/flow/`)
- **FlowFactory**: Creates different flow types (PLANNING, EXECUTION)
- **Planning Flow**: Multi-agent coordination with timeout handling (3600s default)
- **Base Flow**: Abstract foundation for orchestrating agent interactions

#### Sandbox Environment (`OpenManus/app/sandbox/`)
- **Docker Integration**: Containerized execution environment for safety
- **Terminal Management**: Secure command execution with proper cleanup
- **Client-Server Architecture**: Sandbox manager with cleanup lifecycle

### Enhanced Agent Integration Pattern
The enhanced agent demonstrates a sophisticated three-way integration:

#### DSPy + MCP + OpenManus Integration Architecture
- **DSPy Structured Reasoning** (`enhanced_agent/src/dspy_modules.py`):
  - `QueryAnalysis` signature: Extracts topics, query types, and optimal search terms
  - `InformationSynthesis` signature: Combines external info with query context  
  - `ResponseGeneration` signature: Produces structured answers with confidence levels
  - `StructuredResearchPipeline` module: Complete research workflow orchestration

- **MCP Information Gathering** (`enhanced_agent/src/mcp_client.py`):
  - Multi-server support (Ollama, Playwright, custom endpoints)
  - DSPy-optimized query generation for better information retrieval
  - Configurable timeout and context length handling

- **Integration Layer** (`enhanced_agent/src/dspy_mcp_integration.py`):
  - `DSPyMCPIntegration` class orchestrates the complete pipeline
  - Intelligent search term generation from DSPy analysis
  - Multi-step information gathering with result synthesis
  - Fallback modes when components are unavailable

- **OpenManus ReAct Execution** (`enhanced_agent/src/app.py`):
  - `EnhancedResearchAgent` extends ReAct pattern with DSPy pipeline
  - State management for multi-step research workflows
  - Graceful degradation when DSPy is unavailable

## Configuration Management

### LLM Provider Configuration
Both projects support multiple LLM providers via TOML configuration:

#### Supported Providers
- **OpenAI**: Standard OpenAI API
- **Anthropic**: Claude models (recommended default)
- **Azure OpenAI**: Enterprise Azure deployment
- **Ollama**: Local LLM deployment

#### Configuration Example (`OpenManus/config/config.toml`)
```toml
[llm]
model = "claude-3-7-sonnet-20250219"
base_url = "https://api.anthropic.com/v1/"
api_key = "YOUR_API_KEY"
max_tokens = 8192
temperature = 0.0

[llm.vision]
model = "claude-3-7-sonnet-20250219"
base_url = "https://api.anthropic.com/v1/"
api_key = "YOUR_API_KEY"
```

### MCP Server Configuration
Configure external information sources via JSON (`enhanced_agent/config/mcp.json`):
```json
{
  "servers": {
    "llama-mcp": {
      "url": "http://localhost:11434",
      "model": "gemma2:2b",
      "context_length": 4096,
      "temperature": 0.7
    }
  },
  "default_server": "llama-mcp"
}
```

## Development Patterns

### Async/Await Architecture
- All agents and tools use async/await for non-blocking operations
- Timeout handling with `asyncio.wait_for()` for long-running operations
- Context managers for resource cleanup (sandbox, state transitions)

### Error Handling and Resilience  
- State-based error recovery in agents
- Duplicate detection and stuck state handling
- Graceful degradation with proper logging
- Sandbox cleanup on exit

### Package Management and Installation
- **Proper Python Packages**: Both OpenManus and enhanced_agent are installable packages with pyproject.toml
- **Editable Installation**: Install with `pip install -e .` for development (changes reflected immediately)
- **Clean Imports**: No sys.path manipulation required after installation
  - OpenManus: `from openmanus import Manus, ReActAgent`
  - Enhanced Agent: `from enhanced_agent.src.app import run_enhanced_agent`
- **UV-based Dependencies**: Fast dependency resolution and virtual environment management
- **Lock Files**: Requirements pinning for reproducible builds (`make lock`)
- **Dependency Chain**: enhanced_agent depends on openmanus (install openmanus first)

## Testing and Quality Assurance

### Testing Framework
- **pytest** with async support (`pytest-asyncio`) for all async components
- **Test Categories**: Unit tests (`-m unit`), integration tests (`-m integration`), slow tests (`-m slow`)
- **Consolidated Testing**: Root-level pytest configuration for cross-project testing
- **Coverage**: HTML and terminal coverage reporting (`make test-coverage`)

### Test Execution
```bash
make test                    # All tests
make test-unit              # Unit tests only
make test-integration       # Integration tests only
make test-fast              # Exclude slow tests
pytest OpenManus/tests/     # OpenManus specific
pytest enhanced_agent/tests/ # Enhanced agent specific
```

### Code Quality
- **Black + isort**: Automated code formatting (`make format`)
- **Flake8**: Style and error checking (`make lint`)
- **Pre-commit Hooks**: Quality checks before commits (noted in OpenManus README)

## Common Development Workflows

### Setting Up Development Environment
```bash
# Quick setup (recommended)
make install

# Manual setup - install both packages in editable mode
pip install -e OpenManus
pip install -e enhanced_agent

# With all optional dependencies
pip install -e "OpenManus[dev,dspy]"
pip install -e "enhanced_agent[dev]"

# Alternative: using uv for faster installs
uv pip install -e OpenManus
uv pip install -e enhanced_agent
```

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

### Running the Enhanced Research Agent
```bash
# Streamlit web interface (recommended)
./run_streamlit.sh

# Command-line interface
python enhanced_agent/main.py

# Testing components
python test_dspy_standalone.py
```

### Development and Testing Cycle
```bash
# Make changes to code
make format              # Format code
make lint               # Check style
make test-fast          # Quick tests
make test               # Full test suite
```

## Common Issues and Prerequisites

### External Dependencies
- **Ollama**: Required for MCP integration (port 11434)
- **Docker**: Required for sandbox environment
- **Playwright**: Browser automation dependencies
- **API Keys**: LLM provider API keys in configuration files

### Environment Variables
```bash
export OPENAI_API_KEY="your-key"     # For DSPy structured reasoning
# Configure other LLM providers in config.toml files
```

### Virtual Environment Management
The project uses UV for fast package management, but standard pip/conda also work:
```bash
# UV (recommended)
uv venv --python 3.12 && source .venv/bin/activate

# Traditional
python -m venv venv && source venv/bin/activate
```

## Integration Points

### Enhanced Agent as OpenManus Tool
The enhanced agent is integrated into OpenManus as a tool (`OpenManus/app/tool/enhanced_agent_tool.py`), allowing the main agent to delegate complex research tasks when needed.

### Streamlit Interface Integration
The `./run_streamlit.sh` script provides a web interface that combines all capabilities in a user-friendly format, automatically handling virtual environment activation and dependency checks.