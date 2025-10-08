# 🤖 OMD: Enhanced Research Agent

> **OpenManus + DSPy + MCP Integration** - A powerful AI research agent combining structured reasoning, multi-source information gathering, and browser automation.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Overview

OMD is an advanced AI research agent that combines three powerful technologies:

- **🤖 OpenManus**: Multi-modal AI agent framework with browser automation and tool integration
- **🧠 DSPy**: Structured reasoning and prompt optimization for intelligent query analysis
- **🔍 MCP (Model Control Protocol)**: Multi-server information gathering from diverse sources

The system provides both CLI and web interfaces for AI-powered research, analysis, creative problem-solving, and decision support.

## ✨ Key Features

- **Multi-Modal Research** - Handle factual, analytical, and creative queries
- **Structured Responses** - Direct answers, key insights, supporting information, and actionable next steps
- **Browser Automation** - Web scraping and interaction via browser-use integration
- **Session Tracking** - Full Langfuse observability for conversation analysis
- **Graceful Degradation** - Works with or without OpenAI API key
- **Multiple Interfaces** - CLI, Streamlit web UI, and programmatic API
- **Multi-Server Support** - Ollama, web search, Wikipedia, arXiv, news, and more

## 🚀 Quick Start

### Prerequisites

- **Python 3.11-3.13**
- **Ollama** (for local LLM server)
- **Virtual environment** recommended

### Installation

```bash
# Clone the repository
git clone https://github.com/rayhunter/omd.git
cd omd

# Install dependencies
make install

# Or manually:
source virtual/bin/activate
pip install -e enhanced_agent/
pip install -r enhanced_agent/requirements.txt
```

### Configuration

```bash
# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys:
# OPENAI_API_KEY=your_key_here (optional, for enhanced DSPy performance)
# LANGFUSE_PUBLIC_KEY=your_key_here (optional, for observability)
# LANGFUSE_SECRET_KEY=your_key_here (optional, for observability)

# Configure MCP servers (optional)
# Edit enhanced_agent/config/mcp.json to customize information sources
```

### Running the Application

**Option 1: Streamlit Web Interface (Recommended)**
```bash
./run_streamlit.sh
# Opens http://localhost:8501
```

**Option 2: Command Line Interface**
```bash
python enhanced_agent/main.py
```

**Option 3: Python API**
```python
import asyncio
from enhanced_agent.src.app import run_enhanced_agent

async def research(query):
    result = await run_enhanced_agent(query)
    return result

answer = asyncio.run(research("What is quantum computing?"))
print(answer)
```

## 📖 Documentation

## Additionally

- **cd /Users/raymondhunter/LocalProjects/10workspaceOct25/omd**
- **source virtual/bin/activate**
- **streamlit run enhanced_agent_streamlit.py**

### Core Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Detailed setup and usage examples
- **[Development Guide](docs/DEVELOPMENT.md)** - Build system, testing, and contribution guidelines
- **[Observability Guide](docs/OBSERVABILITY.md)** - Langfuse integration and session tracking
- **[Integration Guide](docs/INTEGRATION.md)** - OpenManus tool integration details

### Component Documentation

- **[Enhanced Agent](enhanced_agent/README.md)** - Package-specific documentation
- **[Testing](tests/README.md)** - Test suite and testing guidelines
- **[CLAUDE.md](CLAUDE.md)** - AI assistant guidance for working with this codebase

### Configuration References

- **[MCP Configuration](enhanced_agent/config/README.md)** - Multi-server setup
- **[OpenManus Configuration](OpenManus/config/config.example.toml)** - LLM provider settings

## 🏗️ Architecture

```
User Query
    ↓
┌─────────────────────────────────────────┐
│  Streamlit UI / CLI / API Entry Point   │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  DSPy Query Analysis                    │
│  - Topic extraction                     │
│  - Query type classification            │
│  - Search term generation               │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  MCP Multi-Server Information Gathering │
│  - Ollama (local LLM)                   │
│  - Web search                           │
│  - Wikipedia                            │
│  - arXiv                                │
│  - Custom sources                       │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  OpenManus ReAct Agent                  │
│  - Step-by-step reasoning               │
│  - Tool execution                       │
│  - Browser automation                   │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Structured Response Generation         │
│  - Direct answer                        │
│  - Key insights                         │
│  - Supporting information               │
│  - Actionable next steps                │
└─────────────────────────────────────────┘
    ↓
Langfuse Observability (Session Tracking)
```

## 💡 Usage Examples

### Research Query
```
Q: What are the latest developments in quantum computing?

🧠 DSPy Query Analysis:
   Topic: quantum computing developments
   Type: factual
   Search terms: quantum computing, quantum supremacy, quantum algorithms

🔍 MCP Information Gathering: [3 sources queried]

🎯 Response:
## Direct Answer
Quantum computing has seen significant breakthroughs in 2024, with major
advances in error correction, quantum algorithms, and practical applications...

## Key Insights
- IBM achieved a major milestone with their 1000-qubit processor
- Google demonstrated quantum advantage in optimization problems
- Commercial applications emerging in cryptography and drug discovery

## Next Steps
- Monitor developments in quantum error correction
- Explore potential applications in your field
```

### Analytical Query
```
Q: How can small businesses benefit from AI automation?

📊 Analysis: Business strategy + practical implementation

## Direct Answer
Small businesses can significantly benefit from AI automation through cost
reduction (67% in routine tasks), improved efficiency, and enhanced customer
experience...

## Key Insights
- Customer service chatbots handle 80% of common inquiries
- Predictive analytics optimizes inventory and cash flow
- Start with low-risk, high-impact areas

## Next Steps
1. Identify repetitive tasks suitable for automation
2. Begin with customer service automation
3. Gradually expand to inventory and marketing
```

See [Quick Start Guide](docs/QUICK_START.md) for more examples.

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test categories
pytest -m unit                    # Unit tests only
pytest -m integration             # Integration tests only
pytest -m "not slow"              # Fast tests only

# Run with coverage
make test-coverage
```

See [Testing Guide](tests/README.md) for detailed information.

## 🛠️ Development

### Build System

```bash
make install      # Install all dependencies
make test         # Run test suite
make lint         # Run code linting
make format       # Auto-format code
make clean        # Clean build artifacts
```

### Development Workflow

```bash
# Set up development environment
./scripts/dev.sh setup

# Run development server
./run_streamlit.sh

# Run tests during development
pytest tests/ -v --tb=short
```

See [Development Guide](docs/DEVELOPMENT.md) for detailed workflows.

## 📊 Observability

The application includes full Langfuse integration for:

- **Session Tracking** - Group conversation traces together
- **User Attribution** - Track individual user interactions
- **Performance Metrics** - Analyze latency and token usage
- **Cost Tracking** - Monitor API costs per session/user
- **Debug Tools** - Trace complete conversation flows

See [Observability Guide](docs/OBSERVABILITY.md) for setup and usage.

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Optional: Enhanced DSPy performance
OPENAI_API_KEY=your_openai_api_key

# Optional: Observability
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://us.cloud.langfuse.com

# Optional: Additional MCP servers
NEWS_API_KEY=your_news_api_key
WEATHER_API_KEY=your_weather_api_key
GITHUB_TOKEN=your_github_token
```

### LLM Provider Configuration

Edit `OpenManus/config/config.toml`:

```toml
[llm]
model = "claude-3-7-sonnet-20250219"
base_url = "https://api.anthropic.com/v1/"
api_key = "YOUR_API_KEY"
max_tokens = 8192
temperature = 0.0
```

Supports: OpenAI, Anthropic (Claude), Azure OpenAI, Ollama

### MCP Server Configuration

Edit `enhanced_agent/config/mcp.json`:

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Format code (`make format`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 🐛 Troubleshooting

### Common Issues

**MCP Connection Failed**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Start Ollama if needed
ollama serve

# Pull required model
ollama pull gemma2:2b
```

**Import Errors**
```bash
# Reinstall in development mode
cd enhanced_agent && pip install -e .
cd ../OpenManus && pip install -e .
```

**DSPy Integration Errors**
```bash
# Install DSPy
pip install dspy-ai>=2.0.0

# Set API key (optional, works without it)
export OPENAI_API_KEY="your-key"
```

See [Quick Start Guide](docs/QUICK_START.md) for more troubleshooting tips.

## 📂 Project Structure

```
omd/
├── enhanced_agent/          # Enhanced agent package
│   ├── src/
│   │   ├── app.py          # Main application
│   │   ├── dspy_mcp_integration.py  # DSPy+MCP pipeline
│   │   ├── mcp_client.py   # MCP client
│   │   └── ...
│   ├── config/             # Configuration files
│   └── tests/              # Package tests
├── OpenManus/              # OpenManus framework
│   ├── app/
│   │   ├── agent/         # Agent implementations
│   │   ├── tool/          # Tool integrations
│   │   └── flow/          # Workflow orchestration
│   └── config/            # OpenManus configuration
├── tests/                  # Project-wide tests
├── docs/                   # Documentation
├── scripts/                # Development scripts
├── Makefile               # Build automation
└── run_streamlit.sh       # Streamlit launcher
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenManus](https://github.com/mannaandpoem/OpenManus) - AI agent framework
- [DSPy](https://github.com/stanfordnlp/dspy) - Structured reasoning
- [Langfuse](https://langfuse.com) - LLM observability
- [Ollama](https://ollama.ai) - Local LLM deployment

## 📬 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/rayhunter/omd/issues)
- **Discussions**: [GitHub Discussions](https://github.com/rayhunter/omd/discussions)
- **Documentation**: [Full Documentation](docs/)

---

**Ready to get started?** → [Quick Start Guide](docs/QUICK_START.md)
