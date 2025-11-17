# Installation Guide

This guide explains how to install the OMD workspace packages (OpenManus and enhanced_agent) for development and use.

## Prerequisites

- Python 3.10 or higher
- pip or uv package manager
- Docker (optional, for sandbox features)
- Git

## Quick Start

### Option 1: Using pip (Recommended)

```bash
# From the repository root directory

# 1. Install OpenManus in development mode
cd OpenManus
pip install -e .
cd ..

# 2. Install enhanced_agent in development mode
cd enhanced_agent
pip install -e .
cd ..

# 3. Install development dependencies (optional)
cd OpenManus
pip install -e ".[dev,dspy]"
cd ..

cd enhanced_agent
pip install -e ".[dev]"
cd ..
```

### Option 2: Using uv (Faster)

```bash
# From the repository root directory

# 1. Install OpenManus in development mode
cd OpenManus
uv pip install -e .
cd ..

# 2. Install enhanced_agent in development mode
cd enhanced_agent
uv pip install -e .
cd ..

# 3. Install development dependencies (optional)
cd OpenManus
uv pip install -e ".[dev,dspy]"
cd ..

cd enhanced_agent
uv pip install -e ".[dev]"
cd ..
```

### Option 3: Using the Makefile

```bash
# From the repository root directory
make install
```

## Post-Installation

After installation, you can import packages using clean imports:

```python
# Import OpenManus
from openmanus import Manus, ReActAgent
from openmanus.config import Config
from openmanus.tool import BaseTool

# Import enhanced_agent
from enhanced_agent.src.app import run_enhanced_agent, create_agent
from enhanced_agent.src.dspy_mcp_integration import DSPyMCPIntegration
```

## Configuration

### OpenManus Configuration

1. Copy the example configuration file:
   ```bash
   cp OpenManus/config/config.example.toml OpenManus/config/config.toml
   ```

2. Edit `OpenManus/config/config.toml` with your API keys and settings.

### Enhanced Agent Configuration

1. Configure MCP servers (if using MCP integration):
   ```bash
   # Edit enhanced_agent/config/mcp.json
   ```

2. Set environment variables:
   ```bash
   export OPENAI_API_KEY="your-api-key"  # Optional, for DSPy
   ```

## Running the Applications

### OpenManus

```bash
# Run the main agent
python OpenManus/main.py

# Or use the installed command
openmanus

# Run planning flows
python OpenManus/run_flow.py
```

### Enhanced Agent

```bash
# Run the command-line interface
python enhanced_agent/main.py

# Run the Streamlit web interface
./run_streamlit.sh

# Or directly
streamlit run enhanced_agent_streamlit.py
```

### Demo Scripts

```bash
# Run the demo agent
python demo_agent.py
```

## Running Tests

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run tests with coverage
make test-coverage

# Run tests in a specific package
pytest OpenManus/tests/
pytest enhanced_agent/tests/
pytest tests/
```

## Development Workflow

1. **Install in editable mode** (already done above):
   ```bash
   pip install -e OpenManus
   pip install -e enhanced_agent
   ```

2. **Make changes to the code** - changes are immediately reflected without reinstalling

3. **Run tests** to verify your changes:
   ```bash
   make test
   ```

4. **Format and lint**:
   ```bash
   make format
   make lint
   ```

## Package Structure

After installation, the packages are structured as follows:

```
openmanus/                    # OpenManus package (installed from OpenManus/app/)
├── agent/                    # Agent implementations
├── tool/                     # Tool framework
├── flow/                     # Flow orchestration
├── config.py                 # Configuration management
└── ...

enhanced_agent/               # Enhanced agent package
├── src/
│   ├── app.py               # Main application
│   ├── dspy_mcp_integration.py
│   ├── mcp_client.py
│   └── ...
└── ...
```

## Troubleshooting

### Import Errors

If you encounter import errors after installation:

1. Verify packages are installed:
   ```bash
   pip list | grep -E "openmanus|enhanced-agent"
   ```

2. Reinstall in editable mode:
   ```bash
   pip install -e OpenManus
   pip install -e enhanced_agent
   ```

### Dependency Conflicts

If you have dependency conflicts:

1. Create a fresh virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Reinstall packages:
   ```bash
   pip install -e OpenManus
   pip install -e enhanced_agent
   ```

### Missing Dependencies

If you're missing optional dependencies:

```bash
# Install DSPy support
pip install -e "OpenManus[dspy]"

# Install development tools
pip install -e "OpenManus[dev]"
pip install -e "enhanced_agent[dev]"
```

## Uninstallation

To uninstall the packages:

```bash
pip uninstall openmanus enhanced-agent
```

Note: This removes the installed packages but preserves your source code.

## Additional Resources

- See [CLAUDE.md](CLAUDE.md) for detailed development guidance
- See [OpenManus/README.md](OpenManus/README.md) for OpenManus-specific documentation
- See [Makefile](Makefile) for available make commands
