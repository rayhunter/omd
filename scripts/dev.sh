#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to display help
show_help() {
    echo -e "${YELLOW}Development Script for OpenManus${NC}"
    echo ""
    echo "Usage: ./scripts/dev.sh [command]"
    echo ""
    echo "Available commands:"
    echo "  setup           - Set up the development environment"
    echo "  install         - Install all packages in development mode"
    echo "  install-prod    - Install production dependencies"
    echo "  lock            - Generate lock files"
    echo "  test            - Run tests"
    echo "  lint            - Run linting"
    echo "  format          - Format code"
    echo "  clean           - Clean up"
    echo "  run [module]    - Run a specific module"
    echo "  help            - Show this help message"
}

# Function to run a command with error handling
run_command() {
    echo -e "${GREEN}Running: $@${NC}"
    "$@"
    local status=$?
    if [ $status -ne 0 ]; then
        echo -e "${YELLOW}Error with command: $@${NC}" >&2
        exit $status
    fi
    return $status
}

# Main script
case "$1" in
    setup)
        echo -e "${GREEN}Setting up development environment...${NC}"
        run_command make venv
        run_command make install
        ;;
    install)
        run_command make install
        ;;
    install-prod)
        run_command make install-prod
        ;;
    lock)
        run_command make lock
        ;;
    test)
        run_command make test
        ;;
    lint)
        run_command make lint
        ;;
    format)
        run_command make format
        ;;
    clean)
        run_command make clean
        ;;
    run)
        if [ -z "$2" ]; then
            echo -e "${YELLOW}Please specify a module to run${NC}"
            exit 1
        fi
        shift
        run_command .venv/bin/python -m "$@"
        ;;
    help|*)
        show_help
        ;;
esac

exit 0
