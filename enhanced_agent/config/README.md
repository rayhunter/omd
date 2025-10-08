# Configuration Guide

This directory contains configuration files for the Enhanced Research Agent.

## 📋 Configuration Files

### `mcp.json` - Basic MCP Configuration

Default MCP server configuration for local Ollama integration.

```json
{
  "servers": {
    "llama-mcp": {
      "url": "http://localhost:11434",
      "model": "gemma2:2b",
      "context_length": 4096,
      "temperature": 0.7,
      "max_tokens": 1024
    }
  },
  "default_server": "llama-mcp"
}
```

**Fields:**
- `url`: MCP server endpoint
- `model`: Model name (for Ollama servers)
- `context_length`: Maximum context window
- `temperature`: Sampling temperature (0.0-1.0)
- `max_tokens`: Maximum tokens per response

### `mcp_extended.json` - Extended MCP Configuration

Multi-server configuration with additional information sources.

**Available Servers:**

#### Local LLM
- **llama-mcp**: Ollama local server

#### Web Services
- **web-search**: DuckDuckGo search
- **wikipedia**: Wikipedia API
- **arxiv**: Academic papers from arXiv

#### Data Services
- **finance**: Yahoo Finance data
- **news-api**: News headlines (requires API key)
- **weather**: Weather data (requires API key)

#### Development Tools
- **github**: GitHub API (requires token)

**Example:**
```json
{
  "servers": {
    "web-search": {
      "url": "https://duckduckgo.com",
      "type": "search",
      "timeout": 30
    },
    "wikipedia": {
      "url": "https://en.wikipedia.org/api/rest_v1",
      "type": "wiki",
      "timeout": 20
    }
  },
  "default_server": "web-search"
}
```

## 🔧 Configuration Options

### Server Configuration

Each server supports these options:

```json
{
  "server-name": {
    "url": "string",              // Server endpoint (required)
    "model": "string",            // Model name (Ollama only)
    "type": "string",             // Server type (search, wiki, api)
    "context_length": 4096,       // Context window size
    "temperature": 0.7,           // Sampling temperature
    "max_tokens": 1024,           // Max response tokens
    "timeout": 30,                // Request timeout (seconds)
    "max_retries": 3,             // Retry attempts on failure
    "retry_delay": 1.0,           // Delay between retries (seconds)
    "api_key": "env:VAR_NAME",    // API key (use env: prefix)
    "headers": {                  // Custom HTTP headers
      "User-Agent": "OMD-Agent/1.0"
    }
  }
}
```

### Environment Variable References

Use `env:VAR_NAME` to reference environment variables:

```json
{
  "news-api": {
    "url": "https://newsapi.org/v2",
    "api_key": "env:NEWS_API_KEY"
  }
}
```

### Default Server

Specify which server to use by default:

```json
{
  "default_server": "llama-mcp"
}
```

## 🚀 Usage

### Selecting Configuration

The application automatically loads `mcp.json`. To use extended configuration:

```python
from enhanced_agent.src.enhanced_mcp_client import EnhancedMCPClient

# Use extended configuration
client = EnhancedMCPClient("enhanced_agent/config/mcp_extended.json")
```

### Environment Variables

Set required API keys in `.env`:

```bash
# News API
NEWS_API_KEY=your_news_api_key

# Weather API
WEATHER_API_KEY=your_weather_api_key

# GitHub API
GITHUB_TOKEN=your_github_token
```

## 📝 Creating Custom Servers

### 1. Add Server to Configuration

Edit `mcp.json` or `mcp_extended.json`:

```json
{
  "servers": {
    "my-custom-server": {
      "url": "http://localhost:8080",
      "type": "custom",
      "timeout": 30,
      "api_key": "env:CUSTOM_API_KEY"
    }
  }
}
```

### 2. Implement Server Endpoint

Your server should accept POST requests with JSON payload:

**Request:**
```json
{
  "query": "user query string",
  "context": "optional context",
  "max_tokens": 1024
}
```

**Response:**
```json
{
  "result": "response text",
  "metadata": {
    "source": "my-custom-server",
    "timestamp": "2025-10-07T12:00:00Z",
    "tokens_used": 150
  }
}
```

### 3. Use in Application

```python
result = await client.query("my query", server_name="my-custom-server")
```

## 🔐 Security Best Practices

### API Keys

- **Never commit API keys** to version control
- Use environment variables with `env:` prefix
- Store keys in `.env` file (add to `.gitignore`)
- Rotate keys regularly

### Server URLs

- Use HTTPS for production servers
- Validate SSL certificates
- Implement rate limiting
- Monitor for suspicious activity

### Timeouts and Retries

- Set reasonable timeouts (10-60 seconds)
- Limit retry attempts (3-5 max)
- Implement exponential backoff
- Log failed requests

## 🧪 Testing Configuration

### Validate Configuration

```python
from enhanced_agent.src.enhanced_mcp_client import EnhancedMCPClient

# Load and validate
try:
    client = EnhancedMCPClient("enhanced_agent/config/mcp.json")
    print("✅ Configuration valid")
except Exception as e:
    print(f"❌ Configuration error: {e}")
```

### Test Server Connection

```python
# Test specific server
result = await client.query("test", server_name="llama-mcp")
print(f"Server response: {result}")
```

### Check Available Servers

```python
servers = client.list_servers()
print(f"Available servers: {servers}")

default = client.get_default_server()
print(f"Default server: {default}")
```

## 📚 Examples

### Example 1: Multiple LLM Providers

```json
{
  "servers": {
    "ollama-gemma": {
      "url": "http://localhost:11434",
      "model": "gemma2:2b",
      "temperature": 0.7
    },
    "ollama-llama": {
      "url": "http://localhost:11434",
      "model": "llama3:8b",
      "temperature": 0.5
    },
    "ollama-qwen": {
      "url": "http://localhost:11434",
      "model": "qwen3:14b",
      "temperature": 0.3
    }
  },
  "default_server": "ollama-gemma"
}
```

### Example 2: Multi-Source Research

```json
{
  "servers": {
    "local-llm": {
      "url": "http://localhost:11434",
      "model": "gemma2:2b"
    },
    "academic": {
      "url": "https://export.arxiv.org/api/query",
      "type": "arxiv"
    },
    "reference": {
      "url": "https://en.wikipedia.org/api/rest_v1",
      "type": "wiki"
    },
    "current-events": {
      "url": "https://newsapi.org/v2",
      "type": "news",
      "api_key": "env:NEWS_API_KEY"
    }
  },
  "default_server": "local-llm"
}
```

### Example 3: Development and Production

**config/mcp.development.json:**
```json
{
  "servers": {
    "dev-server": {
      "url": "http://localhost:11434",
      "model": "gemma2:2b",
      "timeout": 60,
      "max_retries": 5
    }
  }
}
```

**config/mcp.production.json:**
```json
{
  "servers": {
    "prod-server": {
      "url": "https://api.production.com",
      "api_key": "env:PROD_API_KEY",
      "timeout": 30,
      "max_retries": 3,
      "headers": {
        "X-Environment": "production"
      }
    }
  }
}
```

## 🐛 Troubleshooting

### Configuration Not Loading

```bash
# Check file exists and is valid JSON
cat enhanced_agent/config/mcp.json | python -m json.tool
```

### Server Connection Failed

```bash
# Test server endpoint
curl http://localhost:11434/api/version

# Check Ollama is running
ps aux | grep ollama
```

### API Key Issues

```bash
# Verify environment variable is set
echo $NEWS_API_KEY

# Check .env file
cat .env | grep API_KEY
```

### Timeout Errors

- Increase `timeout` value in configuration
- Check network connectivity
- Verify server is responding
- Consider increasing `max_retries`

## 📖 Additional Resources

- [Main README](../../README.md)
- [Integration Guide](../../docs/INTEGRATION.md)
- [Quick Start Guide](../../docs/QUICK_START.md)

---

**Questions?** Open an issue on [GitHub](https://github.com/rayhunter/omd/issues).
