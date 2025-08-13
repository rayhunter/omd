# OpenManus Project Automation

This document describes the automation setup for the OpenManus project.

## Prerequisites

- Python 3.12+
- `uv` package manager (install with `curl -sSf https://astral.sh/uv/install.sh | sh`)
- Make (usually pre-installed on Unix-like systems)

## Setup

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd omd
   ```

2. **Set up the development environment**:
   ```bash
   ./scripts/dev.sh setup
   ```
   This will:
   - Create a virtual environment
   - Install all dependencies in development mode
   - Set up pre-commit hooks

## Development Workflow

### Using the Makefile

```bash
# Install all packages in development mode
make install

# Run tests
make test

# Run linting
make lint

# Format code
make format

# Clean up
make clean
```

### Using the Dev Script

The `dev.sh` script provides a more convenient interface for common tasks:

```bash
# Show help
./scripts/dev.sh help

# Set up the environment (first time)
./scripts/dev.sh setup

# Run tests
./scripts/dev.sh test

# Run a specific module
./scripts/dev.sh run openmanus.module_name
```

## Project Structure

- `OpenManus/` - Main package
- `enhanced_agent/` - Enhanced agent package
- `scripts/` - Automation scripts
  - `dev.sh` - Main development script
- `Makefile` - Common tasks automation

## Lock Files

Lock files are used to ensure reproducible builds. To update them:

```bash
make lock
```

## CI/CD Integration

The project is set up to work with most CI/CD systems. The following environment variables can be used:

- `UV_INDEX_URL`: Custom PyPI index URL
- `UV_EXTRA_INDEX_URL`: Additional package indexes
- `UV_NO_CACHE`: Set to 1 to disable caching

## Troubleshooting

- If you encounter permission issues, try running with `bash` explicitly:
  ```bash
  bash scripts/dev.sh setup
  ```

- To start fresh:
  ```bash
  make clean
  ./scripts/dev.sh setup
  ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
