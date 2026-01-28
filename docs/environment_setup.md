# Environment Setup for Enhanced MCP Servers

To enable all MCP servers, you can optionally set up API keys for external services. The system works without these keys, but some servers will show errors.

## Setting Up API Keys

Create a `.env` file in the project root with the following optional keys:

```bash
# News API (for news-api server)
# Get your free API key from: https://newsapi.org/
NEWS_API_KEY=your_news_api_key_here

# OpenWeatherMap API (for weather server)  
# Get your free API key from: https://openweathermap.org/api
WEATHER_API_KEY=your_weather_api_key_here

# GitHub Token (for github server - optional, increases rate limits)
# Generate a personal access token from: https://github.com/settings/tokens
GITHUB_TOKEN=your_github_token_here

# Optional: OpenAI API Key (for enhanced DSPy performance)
OPENAI_API_KEY=your_openai_api_key_here
```

## Alternatively, set environment variables:

```bash
export NEWS_API_KEY="your_key_here"
export WEATHER_API_KEY="your_key_here"  
export GITHUB_TOKEN="your_token_here"
export OPENAI_API_KEY="your_key_here"
```

## Which servers work without API keys:

- ✅ **llama-mcp**: Local Ollama (always works)
- ✅ **web-search**: DuckDuckGo (no API key needed)
- ✅ **wikipedia**: Wikipedia API (no API key needed)
- ✅ **arxiv**: arXiv API (no API key needed)
- ✅ **finance**: Yahoo Finance (no API key needed)
- ❌ **news-api**: Requires NEWS_API_KEY
- ❌ **weather**: Requires WEATHER_API_KEY
- ⚠️ **github**: Works without key but with lower rate limits

The Enhanced Research Agent will automatically skip servers that require missing API keys and use available ones.
