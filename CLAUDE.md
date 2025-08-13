# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This workspace contains multiple AI/ML development projects, web applications, and tools for various automation and data processing tasks.

## Key Projects

### OpenManus (General AI Agent Framework)
- **Location**: `omd/OpenManus/`
- **Type**: Python-based multi-modal AI agent system with browser automation and tool integration
- **Commands**:
  - `pip install -r requirements.txt` - Install dependencies 
  - `python main.py` - Run basic agent (terminal input)
  - `python run_flow.py` - Run planning flow (recommended, includes timeout handling)
  - `pytest` - Run tests
- **Configuration**: Copy `config/config.example.toml` to `config/config.toml` and configure LLM API keys
- **Environment**: Requires LLM API keys (supports OpenAI, Anthropic, Azure, Ollama)
- **Architecture**: Agent-based with tool collection, browser automation via browser-use, sandbox support

### Enhanced MCP Agent with DSPy Integration
- **Location**: `enhanced_agent/` (complete package with DSPy modules)
- **Type**: Research agent combining OpenManus ReAct + DSPy structured reasoning + MCP integration
- **Commands**:
  - `python enhanced_agent/main.py` - Run enhanced research agent with full DSPy pipeline
  - `python enhanced_agent/src/app.py` - Alternative entry point
  - `python test_dspy_standalone.py` - Test DSPy integration without dependencies
- **Dependencies**: 
  - `dspy-ai>=2.0.0` - Structured reasoning and prompt optimization
  - OpenManus ReAct agent framework
  - MCP client for external information gathering
- **Architecture**: 
  - **Query Analysis**: DSPy signatures for structured query understanding
  - **Information Gathering**: MCP client with intelligent search term generation  
  - **Synthesis**: DSPy modules for information integration and reasoning
  - **Response Generation**: Structured output with confidence levels and actionable insights

## Development Commands

### Build System (Using Makefile and UV)
The repository uses a unified build system with both Makefile and shell scripts:
- `make install` - Install all packages in development mode using uv
- `make test` - Run all tests across projects (uses pytest with async support)
- `make lint` - Run linting (black, flake8, isort)
- `make format` - Auto-format code (black, isort)
- `make lock` - Generate requirements.lock files from pyproject.toml
- `make clean` - Clean up virtual environments and cache files
- `./scripts/dev.sh setup` - Set up complete development environment
- `./scripts/dev.sh run [module]` - Run specific modules

### Individual Project Commands

#### OpenManus Agent Development
1. **Setup**: Copy `OpenManus/config/config.example.toml` to `OpenManus/config/config.toml` and configure LLM API keys
2. **Installation**: 
   - Recommended: `cd OpenManus && uv venv --python 3.12 && source .venv/bin/activate && uv pip install -r requirements.txt`
   - Alternative: `pip install -r OpenManus/requirements.txt`
3. **Running**:
   - `python OpenManus/main.py` - Basic agent with terminal input
   - `python OpenManus/run_flow.py` - Advanced planning flows with 1-hour timeout handling (recommended)
4. **Testing**: `pytest OpenManus/tests/` (supports async tests with pytest-asyncio)

#### Enhanced MCP Agent with DSPy Integration
1. **Setup**: 
   - `cd enhanced_agent && pip install -e .`
   - `pip install dspy-ai>=2.0.0` (for structured reasoning)
2. **Configuration**: 
   - Edit `enhanced_agent/config/mcp.json` for MCP servers (requires Ollama on port 11434)
   - Set OpenAI API key for DSPy: `export OPENAI_API_KEY=your_key` (optional, falls back to basic mode)
3. **Running**: 
   - `python enhanced_agent/main.py` - Full integration with DSPy+MCP+OpenManus
   - `python test_dspy_standalone.py` - Test components independently  
4. **Architecture**: Three-layer integration:
   - **OpenManus Layer**: ReAct agent execution and step management
   - **DSPy Layer**: Structured reasoning with signatures (QueryAnalysis, InformationSynthesis, ResponseGeneration)
   - **MCP Layer**: External information gathering with intelligent query optimization

## Common Patterns

- **Configuration Files**: TOML and JSON configs for LLM API keys and service settings
- **Multi-LLM Support**: Projects support OpenAI, Anthropic, Azure OpenAI, and Ollama
- **Agent Architectures**: ReAct pattern, tool-calling agents, and planning-based flows
- **Tool Integration**: File operations, web browsing, Python execution, and search capabilities
- **Async/Await**: Extensive use of async patterns for concurrent operations

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

#### OpenManus + DSPy + MCP Integration Architecture
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

### Project Structure Patterns
- **Dual Package Layout**: Both OpenManus and enhanced_agent use pyproject.toml with setuptools
- **Config Management**: TOML files for LLM settings, JSON for service configurations  
- **Virtual Environment**: UV-based dependency management with lock files
- **Entry Points**: Multiple entry scripts (main.py for basic, run_flow.py for advanced)

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

### Configuration Management
- Environment-specific config files (example configs provided)
- Multi-LLM provider support (OpenAI, Anthropic, Azure, Ollama)
- Secure API key handling with .toml configuration files

## Testing and Quality Assurance

### Testing Framework
- **pytest** with async support (`pytest-asyncio`) for all async components
- **Test Coverage**: Sandbox operations, MCP integration, agent behaviors
- **Isolation**: Each test component runs in controlled environments

### Code Quality
- **Black + isort**: Automated code formatting
- **Flake8**: Style and error checking  
- **Requirements Locking**: UV-based dependency pinning for reproducible builds
- **Pre-commit Hooks**: Quality checks before commits (noted in OpenManus README)