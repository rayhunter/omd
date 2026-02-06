# Railway Deployment Guide

This guide walks you through deploying the Enhanced Research Agent to Railway.

## Prerequisites

1. A Railway account (https://railway.app)
2. Git repository connected to Railway
3. An LLM API key (OpenAI or Anthropic)

## Required Environment Variables

Configure these in your Railway project settings under "Variables":

### LLM Provider (Required - Choose ONE)

**Option 1: OpenAI**
```
OPENAI_API_KEY=sk-...your-openai-api-key...
OPENAI_MODEL=gpt-4o-mini  # Optional, defaults to gpt-4o-mini
```

**Option 2: Anthropic Claude**
```
ANTHROPIC_API_KEY=sk-ant-...your-anthropic-api-key...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022  # Optional
```

### Observability (Optional)

If you want to use Langfuse for observability:
```
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://us.cloud.langfuse.com  # Optional
```

### MCP Servers (Optional)

If you have external MCP servers, configure them:
```
MCP_SERVER_1_URL=https://your-mcp-server.com
MCP_SERVER_1_API_KEY=your-api-key  # If required
MCP_SERVER_1_MODEL=your-model  # If required
```

## Deployment Steps

### 1. Connect Your Repository

1. Go to Railway dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository

### 2. Configure Environment Variables

1. In your Railway project, go to "Variables" tab
2. Add the required environment variables listed above
3. **CRITICAL**: You MUST set either `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

### 3. Deploy

Railway will automatically:
- Detect the Python application
- Install dependencies from `requirements.txt`
- Run the Streamlit app on the assigned `$PORT`

The deployment should start automatically. Check the logs for:
```
🌍 Environment: cloud
🤖 Using LLM provider: openai (or anthropic)
🤖 Using model: gpt-4o-mini (or your configured model)
✅ DSPy+MCP integration initialized successfully
```

### 4. Access Your App

Once deployed, Railway will provide a public URL like:
```
https://your-app-name.up.railway.app
```

## Troubleshooting

### Issue: "Connection refused" to Ollama

**Symptom**: Logs show:
```
🌍 Environment: local
❌ Error: OllamaException - [Errno 111] Connection refused
```

**Solution**: This means Railway is not detecting the cloud environment or you haven't set an API key.

1. Verify environment detection by checking logs for:
   ```
   🌍 Environment: cloud  # Should say "cloud", not "local"
   ```

2. If it says "local", ensure Railway environment is properly configured
3. Make sure you set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

### Issue: "No LLM provider configured"

**Symptom**: Logs show:
```
⚠️  WARNING: Running in cloud environment but no LLM API keys found!
❌ CRITICAL: No LLM provider configured!
```

**Solution**: Add either `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` to Railway environment variables.

### Issue: DSPy pipeline fails

**Symptom**: 
```
❌ Error in DSPy query analysis: ...
```

**Solution**: 
1. Check that your API key is valid
2. Ensure you have sufficient API credits
3. Verify the model name is correct

## Architecture

The app automatically detects the deployment environment:

- **Local Development**: Uses Ollama at `localhost:11434`
- **Railway Production**: Uses cloud LLM APIs (OpenAI or Anthropic)

Environment detection checks for:
- `RAILWAY_ENVIRONMENT` (Railway)
- `RAILWAY_PROJECT_ID` (Railway)
- `STREAMLIT_CLOUD` (Streamlit Cloud)

## Cost Considerations

### LLM API Costs

- **OpenAI GPT-4o-mini**: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- **Anthropic Claude 3.5 Sonnet**: ~$3.00 per 1M input tokens, ~$15.00 per 1M output tokens

Typical query costs:
- Simple query (100 tokens in, 300 tokens out): $0.0002 - $0.005
- Complex research (500 tokens in, 2000 tokens out): $0.001 - $0.03

### Railway Hosting Costs

- **Hobby Plan**: $5/month for 500 hours
- **Pro Plan**: $20/month for 500 hours + additional resources

## Security Best Practices

1. **Never commit API keys** to your repository
2. Use Railway's environment variables for all secrets
3. Rotate API keys regularly
4. Monitor API usage to detect anomalies
5. Set API rate limits in your provider dashboard

## Monitoring

### Railway Logs

Access real-time logs in the Railway dashboard:
- Deployment logs
- Application logs
- Error traces

### Langfuse (Optional)

If you configured Langfuse, you can:
- Track all LLM interactions
- Monitor costs per session
- Analyze query performance
- Debug issues with detailed traces

Dashboard: https://us.cloud.langfuse.com

## Support

If you encounter issues:

1. Check Railway deployment logs
2. Verify all environment variables are set correctly
3. Test your API keys locally first
4. Review this troubleshooting guide

## Next Steps

After successful deployment:

1. Test with a simple query
2. Monitor costs in your LLM provider dashboard
3. Configure Langfuse for observability (optional)
4. Set up alerts for errors or high costs
5. Consider caching strategies for frequently asked queries
