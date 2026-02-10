# Railway Deployment - Quick Start

## ✅ Files Ready for Deployment

All deployment configuration files are now in place:

1. **`Procfile`** - Railway start command
2. **`railway.toml`** - Railway configuration
3. **`Dockerfile`** - Optional Docker build
4. **`.dockerignore`** - Optimizes Docker builds

## 🚀 Deploy to Railway in 3 Steps

### Step 1: Set Environment Variables in Railway

**REQUIRED** (choose one):
```
OPENAI_API_KEY=sk-...
```
OR
```
ANTHROPIC_API_KEY=sk-ant-...
```

**OPTIONAL** (for enhanced features):
```
NEWS_API_KEY=...                # News queries
OPENWEATHER_API_KEY=...         # Weather queries
LANGFUSE_PUBLIC_KEY=pk-lf-...   # Observability
LANGFUSE_SECRET_KEY=sk-lf-...   # Observability
```

### Step 2: Push to GitHub

```bash
git add Procfile railway.toml Dockerfile .dockerignore
git commit -m "Add Railway deployment configuration"
git push origin main
```

### Step 3: Deploy on Railway

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway auto-deploys from your `main` branch

That's it! ✨

## 📊 Expected Deployment Timeline

- **Build**: 2-3 minutes (first time)
- **Startup**: 10-20 seconds
- **Total**: ~3 minutes from push to live

## ✅ Verification Checklist

After deployment, check Railway logs for:

```
✅ Environment variables loaded from .env file
🌍 Environment: cloud
🤖 Using LLM provider: openai
🤖 Using model: gpt-4o-mini
MCP Client initialized with 5 enabled servers: web-search, wikidata, dbpedia, arxiv, news-api
✅ DSPy+MCP integration initialized successfully
✅ Configuration helper loaded
```

Then visit your Railway URL and test a query!

## 🔧 Build Options

Railway supports two build methods:

### Option 1: Nixpacks (Default, Recommended)
- Uses `Procfile` automatically
- Faster builds
- No configuration needed

### Option 2: Docker
- Uses `Dockerfile` if present
- More control over environment
- Slightly slower builds

To force Docker builds, add this to `railway.toml`:
```toml
[build]
builder = "DOCKERFILE"
```

## 🐛 Troubleshooting

### Build Fails
- Check `requirements.txt` is valid
- Verify all dependencies are available on PyPI
- Check Railway build logs for specific errors

### App Won't Start
- Verify `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is set
- Check Railway logs for startup errors
- Ensure port binding is correct (uses `$PORT`)

### Health Check Fails
- Wait 40 seconds for startup (configured in `railway.toml`)
- Check if Streamlit is actually running
- Verify `/_stcore/health` endpoint is accessible

### "Connection Refused" Errors
- Ensure you set an API key (not using Ollama)
- Verify environment is detected as "cloud" (check logs)
- Confirm MCP servers are cloud-compatible (no localhost)

## 📈 Monitoring

### Railway Dashboard
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: History and rollback options

### Application Logs
Watch for these indicators:
- ✅ Environment detection
- ✅ LLM provider initialization
- ✅ MCP server counts
- ✅ Query processing times

## 💰 Cost Estimation

### Railway Hosting
- **Hobby Plan**: $5/month (500 hours)
- **Pro Plan**: $20/month (includes more resources)

### LLM API Costs
- **OpenAI gpt-4o-mini**: ~$0.15/$0.60 per 1M tokens (in/out)
- **Anthropic Claude 3.5**: ~$3/$15 per 1M tokens (in/out)

**Typical Query Cost**: $0.0002 - $0.005 per query

## 🎯 Next Steps

After successful deployment:

1. **Test basic queries**: Verify functionality
2. **Monitor costs**: Check API usage
3. **Add API keys**: Enable weather/news features (optional)
4. **Set up Langfuse**: Enable observability (optional)
5. **Optimize performance**: Add caching (see Lighthouse optimization plan)

## 📚 Related Documentation

- `RAILWAY_DEPLOYMENT.md` - Complete deployment guide
- `MCP_ERROR_FIX.md` - MCP troubleshooting
- `TIMER_FEATURE_SUMMARY.md` - Timer feature docs

## ✨ Ready to Deploy!

All configuration files are in place. Just set your API keys in Railway and push to deploy! 🚀
