# 🛠️ Development Guide

This guide covers development workflows, build automation, testing, and contribution guidelines for the OMD project.

## 📋 Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Build System](#build-system)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Development Workflows](#development-workflows)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## 🚀 Development Environment Setup

### Prerequisites

- **Python 3.11-3.13**
- **uv package manager** (recommended) or pip
- **Make** (usually pre-installed on Unix-like systems)
- **Git**
- **Ollama** (for MCP integration)

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/rayhunter/omd.git
cd omd

# Set up development environment
./scripts/dev.sh setup

# This will:
# - Create virtual environment
# - Install all dependencies in development mode
# - Set up pre-commit hooks
```

### Manual Setup

```bash
# Create virtual environment
python -m venv virtual
source virtual/bin/activate  # On Windows: virtual\Scripts\activate

# Install packages in development mode
cd enhanced_agent && pip install -e . && cd ..
cd OpenManus && pip install -e . && cd ..

# Install all dependencies
pip install -r enhanced_agent/requirements.txt
pip install -r OpenManus/requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio pytest-cov black flake8 isort
```

### Using UV (Recommended)

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment with UV
uv venv --python 3.12
source .venv/bin/activate

# Install dependencies with UV (faster)
uv pip install -r enhanced_agent/requirements.txt
uv pip install -r OpenManus/requirements.txt
```

## 🏗️ Build System

### Makefile Commands

The project uses a Makefile for common development tasks:

```bash
# Installation
make install              # Install all packages in development mode
make install-dev          # Install with development dependencies

# Testing
make test                 # Run all tests
make test-unit           # Run unit tests only
make test-integration    # Run integration tests only
make test-fast           # Run fast tests (exclude slow tests)
make test-coverage       # Run tests with coverage reporting

# Code Quality
make lint                 # Run linting (black, flake8, isort)
make format              # Auto-format code
make check               # Run linting without making changes

# Maintenance
make clean               # Clean build artifacts and cache
make lock                # Update lock files
make update              # Update dependencies
```

### Dev Script Commands

The `scripts/dev.sh` script provides a convenient interface:

```bash
# Help and documentation
./scripts/dev.sh help

# Setup and installation
./scripts/dev.sh setup              # Complete environment setup
./scripts/dev.sh install            # Install dependencies

# Testing
./scripts/dev.sh test               # Run all tests
./scripts/dev.sh test unit          # Run unit tests
./scripts/dev.sh test integration   # Run integration tests

# Running
./scripts/dev.sh run enhanced_agent.main    # Run specific module
./scripts/dev.sh streamlit                  # Start Streamlit interface

# Code quality
./scripts/dev.sh lint               # Run linting
./scripts/dev.sh format             # Format code
```

## 🧪 Testing

### Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_enhanced_agent.py
│   └── test_dspy_standalone.py
└── integration/             # Integration tests
    ├── test_dspy_integration.py
    ├── test_multi_mcp.py
    └── test_enhanced_agent_integration.py
```

### Running Tests

```bash
# All tests
make test
# or
pytest

# Specific test categories
pytest -m unit                   # Unit tests only
pytest -m integration            # Integration tests only
pytest -m "not slow"             # Fast tests only

# Specific test file
pytest tests/unit/test_enhanced_agent.py

# With verbose output
pytest -v

# With coverage
make test-coverage
# or
pytest --cov=enhanced_agent --cov=OpenManus --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Test Markers

Tests are automatically marked based on location and content:

- `@pytest.mark.unit` - Unit tests (in tests/unit/)
- `@pytest.mark.integration` - Integration tests (in tests/integration/)
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.requires_api` - Tests requiring external APIs

### Writing Tests

```python
import pytest
from enhanced_agent.src.app import EnhancedResearchAgent

@pytest.mark.unit
def test_agent_initialization(mock_dspy_settings):
    """Test that agent initializes correctly."""
    agent = EnhancedResearchAgent()
    assert agent is not None

@pytest.mark.integration
@pytest.mark.slow
async def test_full_research_workflow(sample_test_queries):
    """Test complete research workflow."""
    agent = EnhancedResearchAgent()
    result = await agent.process(sample_test_queries["factual"])
    assert "Direct Answer" in result
```

### Using Test Fixtures

Available fixtures in `conftest.py`:

```python
def test_with_fixtures(
    project_root,           # Path to project root
    mock_openai_api,        # Mock OpenAI API
    mock_mcp_client,        # Mock MCP client
    sample_test_queries,    # Sample queries
    mock_dspy_settings      # Mock DSPy settings
):
    # Your test code
    pass
```

## 📐 Code Quality

### Linting

```bash
# Run all linters
make lint

# Individual linters
black --check .              # Check formatting
flake8 .                     # Check style
isort --check-only .         # Check import order
```

### Auto-formatting

```bash
# Format all code
make format

# Individual formatters
black .                      # Format with black
isort .                      # Sort imports
```

### Code Style Guidelines

- **PEP 8** compliance
- **Black** formatter with default settings
- **Import order**: Standard library, third-party, local
- **Line length**: 88 characters (Black default)
- **Docstrings**: Google style

Example:

```python
"""Module docstring explaining the module purpose.

This module provides functionality for X, Y, and Z.
"""

from typing import Optional
import asyncio

from enhanced_agent.src import utils


class MyClass:
    """Class docstring explaining the class.

    Attributes:
        attribute_name: Description of attribute
    """

    def my_method(self, param: str) -> Optional[str]:
        """Method docstring.

        Args:
            param: Description of parameter

        Returns:
            Description of return value

        Raises:
            ValueError: When parameter is invalid
        """
        pass
```

## 🔄 Development Workflows

### Feature Development

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes
# Edit files...

# 3. Format and lint
make format
make lint

# 4. Run tests
make test-fast          # Quick check
make test               # Full test suite

# 5. Commit changes
git add .
git commit -m "feat: add my feature"

# 6. Push and create PR
git push origin feature/my-feature
```

### Bug Fix Workflow

```bash
# 1. Create bug fix branch
git checkout -b fix/issue-123

# 2. Write failing test
# Add test that reproduces the bug

# 3. Fix the bug
# Edit code to fix

# 4. Verify fix
pytest tests/test_specific.py -v

# 5. Run full test suite
make test

# 6. Commit and push
git add .
git commit -m "fix: resolve issue #123"
git push origin fix/issue-123
```

### Testing Workflow

```bash
# Watch mode for continuous testing
pytest --watch

# Test specific functionality
pytest tests/unit/test_enhanced_agent.py::test_specific_function -v

# Debug test failures
pytest --pdb                 # Drop into debugger on failure
pytest -vv                   # Very verbose output
pytest --tb=short            # Short traceback
```

### Documentation Workflow

```bash
# Update documentation
# Edit docs/*.md files

# Check documentation links
make check-docs

# Preview documentation locally
# (if using mkdocs or similar)
mkdocs serve
```

## 📁 Project Structure

```
omd/
├── enhanced_agent/              # Main package
│   ├── src/
│   │   ├── app.py              # Application entry
│   │   ├── dspy_mcp_integration.py
│   │   ├── mcp_client.py
│   │   └── enhanced_mcp_client.py
│   ├── config/                 # Configuration files
│   │   ├── mcp.json
│   │   └── mcp_extended.json
│   ├── tests/                  # Package tests
│   └── requirements.txt
├── OpenManus/                   # OpenManus framework
│   ├── app/
│   │   ├── agent/              # Agent implementations
│   │   ├── tool/               # Tool integrations
│   │   ├── flow/               # Workflow orchestration
│   │   └── sandbox/            # Sandbox environment
│   ├── config/                 # OpenManus config
│   └── requirements.txt
├── tests/                       # Project-wide tests
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── docs/                        # Documentation
│   ├── QUICK_START.md
│   ├── DEVELOPMENT.md
│   ├── OBSERVABILITY.md
│   └── INTEGRATION.md
├── scripts/                     # Development scripts
│   └── dev.sh
├── Makefile                     # Build automation
├── pytest.ini                   # Pytest configuration
├── pyproject.toml              # Project metadata
├── .env.example                # Environment template
└── README.md                   # Main documentation
```

## 🤝 Contributing

### Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/omd.git`
3. Set up development environment: `./scripts/dev.sh setup`
4. Create a feature branch: `git checkout -b feature/my-feature`

### Commit Guidelines

Use conventional commits:

```bash
feat: Add new feature
fix: Fix bug
docs: Update documentation
test: Add or update tests
refactor: Code refactoring
style: Code style changes
chore: Maintenance tasks
```

### Pull Request Process

1. **Ensure tests pass**: `make test`
2. **Format code**: `make format`
3. **Update documentation** if needed
4. **Create PR** with clear description
5. **Respond to review feedback**

### Code Review Checklist

- [ ] Tests pass locally
- [ ] Code is formatted (black, isort)
- [ ] Linting passes (flake8)
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] No merge conflicts
- [ ] Changes are focused and atomic

## 🐛 Debugging

### Debug Mode

```bash
# Run with debug logging
export DEBUG=1
python enhanced_agent/main.py

# Python debugger
import pdb; pdb.set_trace()

# Pytest with debugger
pytest --pdb
```

### Common Issues

**Import Errors**
```bash
# Reinstall in development mode
pip install -e enhanced_agent/
pip install -e OpenManus/
```

**Test Failures**
```bash
# Run with more verbosity
pytest -vvs

# Check fixtures
pytest --fixtures

# Clear cache
pytest --cache-clear
```

**Virtual Environment Issues**
```bash
# Clean and recreate
rm -rf virtual
python -m venv virtual
source virtual/bin/activate
pip install -r enhanced_agent/requirements.txt
```

## 📚 Additional Resources

- [Testing Guide](../tests/README.md)
- [CLAUDE.md](../CLAUDE.md) - AI assistant guidance
- [Quick Start](QUICK_START.md)
- [Observability](OBSERVABILITY.md)

---

**Questions?** Open an issue or discussion on GitHub.
