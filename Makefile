# Project configuration
PROJECTS = OpenManus enhanced_agent
VENV = .venv
PYTHON = $(VENV)/bin/python
UV = uv

# Default target
all: install

# Create virtual environment
venv:
	@echo "Creating virtual environment..."
	@$(UV) venv
	@echo "Installing uv tools..."
	@$(UV) pip install --upgrade pip uv

# Install all packages in development mode
install: venv
	@echo "Installing all packages in development mode..."
	@for project in $(PROJECTS); do \
		echo "Installing $$project..."; \
		(cd $$project && $(UV) pip install -e .); \
	done

# Install production dependencies
install-prod: venv
	@echo "Installing production dependencies..."
	@for project in $(PROJECTS); do \
		echo "Installing $$project..."; \
		(cd $$project && $(UV) pip install .); \
	done

# Generate lock files
lock:
	@echo "Generating lock files..."
	@for project in $(PROJECTS); do \
		echo "Generating lock file for $$project..."; \
		(cd $$project && $(UV) pip compile -o requirements.lock pyproject.toml); \
	done

# Run tests
test: install
	@echo "Running tests..."
	@for project in $(PROJECTS); do \
		echo "Testing $$project..."; \
		(cd $$project && $(PYTHON) -m pytest -v || exit 1); \
	done

# Run linting
lint: install
	@echo "Running linting..."
	@$(UV) pip install black flake8 isort
	@for project in $(PROJECTS); do \
		echo "Linting $$project..."; \
		(cd $$project && black --check . && flake8 . && isort --check-only .) || exit 1; \
	done

# Format code
format:
	@echo "Formatting code..."
	@$(UV) pip install black isort
	@for project in $(PROJECTS); do \
		echo "Formatting $$project..."; \
		(cd $$project && black . && isort .); \
	done

# Clean up
clean:
	@echo "Cleaning up..."
	@rm -rf $(VENV)
	@find . -type d -name "__pycache__" -exec rm -r {} +
	@find . -type d -name ".pytest_cache" -exec rm -r {} +
	@find . -type d -name ".mypy_cache" -exec rm -r {} +

# Help message
help:
	@echo "Available commands:"
	@echo "  make install      Install all packages in development mode"
	@echo "  make install-prod Install production dependencies"
	@echo "  make lock         Generate lock files"
	@echo "  make test         Run tests"
	@echo "  make lint         Run linting"
	@echo "  make format       Format code"
	@echo "  make clean        Clean up"

.PHONY: all venv install install-prod lock test lint format clean help
