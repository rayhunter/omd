# Cloud Deployment Guide

This guide explains how to properly configure the Enhanced Research Agent for both local and cloud environments.

## 🏠 **Local Environment (Current Setup)**

### Configuration
- **Model**: `gemma2:2b` (via Ollama)
- **Config**: `.env` file
- **Dependencies**: All installed locally

### How it works
```python
# The app automatically detects it's running locally
environment = "local"
model = "gemma2:2b"  # Uses your local Ollama
```

## ☁️ **Streamlit Cloud Environment**

### Configuration
- **Model**: `microsoft/Phi-3-mini-4k-instruct` (via Hugging Face)
- **Config**: Streamlit secrets
- **Dependencies**: Installed from `requirements.txt`

### How it works
```python
# The app automatically detects it's running in cloud
environment = "cloud"
model = "microsoft/Phi-3-mini-4k-instruct"  # Uses Hugging Face
```

## 🔧 **Configuration Priority**

The app uses this priority order for configuration:

1. **Environment Variables** (highest priority)
2. **Streamlit Secrets** (cloud only)
3. **Default Values** (fallback)

### Environment Variables
```bash
# Set these in your environment
export LLM_MODEL="microsoft/Phi-3-mini-4k-instruct"
export OPENAI_API_KEY="your-key-here"
export LANGFUSE_PUBLIC_KEY="your-key-here"
export LANGFUSE_SECRET_KEY="your-key-here"
```

### Streamlit Secrets
In Streamlit Cloud, add these to your secrets:

```toml
# .streamlit/secrets.toml
LLM_MODEL = "microsoft/Phi-3-mini-4k-instruct"
OPENAI_API_KEY = "your-openai-api-key"
LANGFUSE_PUBLIC_KEY = "your-langfuse-public-key"
LANGFUSE_SECRET_KEY = "your-langfuse-secret-key"
LANGFUSE_HOST = "https://us.cloud.langfuse.com"
```

## 🚀 **Deployment Steps**

### 1. **Prepare for Cloud**
```bash
# The app will automatically use the right model
# No code changes needed!
```

### 2. **Deploy to Streamlit Cloud**
1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Connect your GitHub repository
3. Set main file: `enhanced_agent_streamlit.py`
4. Add secrets (optional, for full functionality)

### 3. **Test Both Environments**
```bash
# Local (uses gemma2:2b)
streamlit run enhanced_agent_streamlit.py

# Cloud (uses microsoft/Phi-3-mini-4k-instruct)
# Deploy to Streamlit Cloud
```

## 📊 **Model Comparison**

| Environment | Model | Size | Speed | Reasoning | Best For |
|-------------|-------|------|-------|-----------|----------|
| Local | gemma2:2b | 2B | ⭐⭐⭐⭐ | ⭐⭐⭐ | Private, fast |
| Cloud | Phi-3-mini | 3.8B | ⭐⭐⭐ | ⭐⭐⭐⭐ | Public, powerful |

## 🔍 **Troubleshooting**

### Common Issues

1. **"No module named 'dotenv'"**
   - ✅ **Fixed**: App now handles missing dotenv gracefully
   - **Solution**: Uses environment variables instead

2. **"Model not found"**
   - ✅ **Fixed**: App automatically selects appropriate model
   - **Solution**: Uses Hugging Face models in cloud

3. **"Configuration not loaded"**
   - ✅ **Fixed**: App uses multiple configuration sources
   - **Solution**: Falls back to defaults if needed

### Debug Information
The app will show:
```
🌍 Environment: local/cloud
🤖 Using model: gemma2:2b/microsoft/Phi-3-mini-4k-instruct
✅ Configuration helper loaded
```

## 🎯 **Expected Behavior**

### Local Environment
- ✅ Uses `gemma2:2b` via Ollama
- ✅ Loads `.env` file
- ✅ Full DSPy structured reasoning
- ✅ Langfuse tracing
- ✅ MCP information gathering

### Cloud Environment
- ✅ Uses `microsoft/Phi-3-mini-4k-instruct` via Hugging Face
- ✅ Loads Streamlit secrets
- ✅ Full DSPy structured reasoning
- ✅ Langfuse tracing (if API keys provided)
- ✅ MCP information gathering

## 💡 **Key Benefits**

1. **Automatic Detection**: App knows which environment it's in
2. **Graceful Fallbacks**: Works even with missing dependencies
3. **No Code Changes**: Same code works in both environments
4. **Optimal Performance**: Uses best model for each environment
5. **Easy Deployment**: Just push to GitHub and deploy

The app is now **truly cloud-ready**! 🎉
