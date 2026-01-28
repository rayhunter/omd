# 📚 Documentation Index

Complete guide to OMD (OpenManus + DSPy + MCP) Enhanced Research Agent documentation.

## 🚀 Getting Started

**New to OMD?** Start here:

1. **[Main README](../README.md)** - Project overview, features, and quick start
2. **[Quick Start Guide](QUICK_START.md)** - Detailed setup and first steps
3. **[Usage Examples](USAGE_EXAMPLES.md)** - Real-world examples and use cases

## 📖 Core Documentation

### For Users

- **[Quick Start Guide](QUICK_START.md)**
  - Prerequisites and installation
  - Running the application (CLI, Web, API)
  - Basic usage and examples
  - Troubleshooting common issues

- **[Usage Examples](USAGE_EXAMPLES.md)**
  - Example conversations
  - Different query types (factual, analytical, creative)
  - Best practices for getting good results
  - Advanced usage patterns

### For Developers

- **[Development Guide](DEVELOPMENT.md)**
  - Development environment setup
  - Build system and automation
  - Testing framework and guidelines
  - Code quality standards
  - Contribution workflow

- **[Integration Guide](INTEGRATION.md)**
  - OpenManus tool integration
  - Creating custom MCP servers
  - API integration patterns
  - Extension points and customization

- **[Observability Guide](OBSERVABILITY.md)**
  - Langfuse setup and configuration
  - Session tracking implementation
  - Dashboard usage and analytics
  - Best practices for monitoring

### Status & Integration Reports

Status files and integration summaries are located in [`docs/status/`](status/):
- Test migration reports
- Integration completion summaries
- Feature status updates
- Upgrade documentation

### Technical Guides

Detailed technical guides are in [`docs/guides/`](guides/):
- Model configuration
- Advanced setup and configuration

### Component Documentation

- **[Enhanced Agent](../enhanced_agent/README.md)**
  - Package-specific documentation
  - Architecture and components
  - Configuration options
  - API reference

- **[Testing Guide](../tests/README.md)**
  - Test structure and organization
  - Running tests
  - Writing new tests
  - Test fixtures and utilities

- **[CLAUDE.md](archive/CLAUDE.md)** (Archived)
  - AI assistant guidance
  - Repository structure for LLM agents
  - Development commands and patterns
  - Architecture overview

## 🔧 Configuration

- **[MCP Configuration](../enhanced_agent/config/README.md)**
  - Multi-server setup
  - Custom server configuration
  - Available MCP servers

- **[OpenManus Configuration](../OpenManus/config/config.example.toml)**
  - LLM provider settings
  - Model configuration
  - API keys and endpoints

- **[Environment Variables](../README.md#configuration)**
  - Required and optional variables
  - API keys setup
  - Service endpoints

## 🎯 By Use Case

### I want to...

#### Run the Application
→ [Quick Start Guide](QUICK_START.md) → [Running the Application](QUICK_START.md#running-the-application)

#### Understand How It Works
→ [Main README](../README.md) → [Architecture](../README.md#architecture)

#### Integrate with My Project
→ [Integration Guide](INTEGRATION.md) → [API Integration](INTEGRATION.md#api-integration)

#### Contribute Code
→ [Development Guide](DEVELOPMENT.md) → [Contributing](DEVELOPMENT.md#contributing)

#### Set Up Monitoring
→ [Observability Guide](OBSERVABILITY.md) → [Quick Start](OBSERVABILITY.md#quick-start)

#### Create a Custom MCP Server
→ [Integration Guide](INTEGRATION.md) → [Custom MCP Servers](INTEGRATION.md#custom-mcp-servers)

#### Write Tests
→ [Development Guide](DEVELOPMENT.md) → [Testing](DEVELOPMENT.md#testing)
→ [Testing Guide](../tests/README.md)

#### Deploy to Production
→ [Development Guide](DEVELOPMENT.md) → [Build System](DEVELOPMENT.md#build-system)
→ [Observability Guide](OBSERVABILITY.md) → [Session Tracking](OBSERVABILITY.md#session-tracking)

#### Troubleshoot Issues
→ [Quick Start Guide](QUICK_START.md) → [Troubleshooting](QUICK_START.md#troubleshooting)
→ [Main README](../README.md) → [Troubleshooting](../README.md#troubleshooting)

## 📁 Documentation Structure

```
docs/
├── INDEX.md                    # This file - documentation map
├── QUICK_START.md             # Getting started guide
├── USAGE_EXAMPLES.md          # Usage examples and patterns
├── DEVELOPMENT.md             # Development and contribution guide
├── INTEGRATION.md             # Integration and extension guide
├── OBSERVABILITY.md           # Monitoring and analytics guide
├── langfuse_session_tracking.md  # Detailed Langfuse guide
└── archive/                   # Old documentation
    ├── QUICK_START_GUIDE.md
    ├── README-AUTOMATION.md
    ├── ENHANCED_AGENT_INTEGRATION.md
    ├── SESSION_TRACKING_SUMMARY.md
    └── CONTEXT_ERROR_FIX.md
```

## 🔍 Quick Reference

### Common Commands

```bash
# Run the app
./run_streamlit.sh          # Streamlit interface
python enhanced_agent/main.py  # CLI interface

# Development
make install                # Install dependencies
make test                   # Run tests
make format                 # Format code

# Testing
pytest -m unit             # Unit tests
pytest -m integration      # Integration tests
```

### Key Files

- **Main Entry**: `enhanced_agent/main.py`
- **Streamlit UI**: `enhanced_agent_streamlit.py`
- **DSPy Pipeline**: `enhanced_agent/src/dspy_mcp_integration.py`
- **MCP Client**: `enhanced_agent/src/mcp_client.py`
- **Configuration**: `enhanced_agent/config/mcp.json`

### Configuration Files

- `.env` - Environment variables and API keys
- `enhanced_agent/config/mcp.json` - MCP server configuration
- `OpenManus/config/config.toml` - OpenManus/LLM configuration
- `pytest.ini` - Test configuration
- `Makefile` - Build automation

## 🆘 Getting Help

### In Order of Preference:

1. **Search this documentation** - Use Ctrl/Cmd+F in your browser
2. **Check the FAQ** in [Quick Start Guide](QUICK_START.md)
3. **Review [Troubleshooting](../README.md#troubleshooting)** sections
4. **Open a [GitHub Issue](https://github.com/rayhunter/omd/issues)**
5. **Start a [GitHub Discussion](https://github.com/rayhunter/omd/discussions)**

### Common Questions

**Q: How do I run the application?**
A: See [Quick Start Guide](QUICK_START.md#running-the-application)

**Q: How do I set up Langfuse tracking?**
A: See [Observability Guide](OBSERVABILITY.md#quick-start)

**Q: How do I create a custom MCP server?**
A: See [Integration Guide](INTEGRATION.md#custom-mcp-servers)

**Q: How do I contribute?**
A: See [Development Guide](DEVELOPMENT.md#contributing)

**Q: Where are the tests?**
A: See [Testing Guide](../tests/README.md)

**Q: How do I use the agent programmatically?**
A: See [Integration Guide](INTEGRATION.md#api-integration)

## 📊 Documentation Coverage

### Complete ✅
- [x] Main README with project overview
- [x] Quick start and installation guide
- [x] Usage examples and patterns
- [x] Development and testing guide
- [x] Integration and extension guide
- [x] Observability and monitoring guide
- [x] Configuration references
- [x] Troubleshooting sections

### Planned 📝
- [ ] API reference documentation
- [ ] Deployment guide (Docker, cloud)
- [ ] Performance tuning guide
- [ ] Security best practices
- [ ] Migration guides
- [ ] Video tutorials
- [ ] Architecture decision records (ADRs)

## 🔄 Documentation Maintenance

### Keeping Docs Up to Date

- Documentation is reviewed with each PR
- Breaking changes require documentation updates
- Examples are tested as part of CI/CD
- User feedback incorporated regularly

### Contributing to Documentation

1. Fork the repository
2. Edit documentation in `docs/` or root
3. Follow markdown style guide
4. Test examples and code snippets
5. Submit PR with clear description

See [Development Guide](DEVELOPMENT.md#contributing) for details.

## 📜 Documentation License

All documentation is licensed under [MIT License](../LICENSE), same as the code.

---

**Can't find what you're looking for?** [Open an issue](https://github.com/rayhunter/omd/issues) or [start a discussion](https://github.com/rayhunter/omd/discussions).
