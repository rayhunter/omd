# Streamlit Cloud Deployment Guide

This guide helps you deploy the Enhanced Research Agent to Streamlit Cloud.

## 🚀 Quick Deployment

1. **Fork this repository** to your GitHub account
2. **Go to [Streamlit Cloud](https://share.streamlit.io/)**
3. **Click "New app"**
4. **Connect your GitHub repository**
5. **Set the following configuration:**

### App Configuration
- **Main file path**: `enhanced_agent_streamlit.py`
- **Python version**: 3.11 or 3.12
- **Requirements file**: `requirements.txt`

### Environment Variables (Optional)
Add these in Streamlit Cloud's secrets management:

```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "your-openai-api-key-here"
LANGFUSE_PUBLIC_KEY = "your-langfuse-public-key"
LANGFUSE_SECRET_KEY = "your-langfuse-secret-key"
LANGFUSE_HOST = "https://us.cloud.langfuse.com"
```

## ⚠️ Important Notes

### Ollama Limitation
- **Ollama models (gemma2:2b) will NOT work** in Streamlit Cloud
- Streamlit Cloud doesn't support local model servers
- The app will fall back to basic MCP responses without DSPy structured reasoning

### Recommended Configuration for Cloud
1. **Set up OpenAI API key** in Streamlit secrets
2. **Update the model** in `enhanced_agent/src/app.py`:
   ```python
   dspy_mcp = DSPyMCPIntegration(
       llm_model="gpt-3.5-turbo",  # Use OpenAI instead of gemma2:2b
       dspy_cache=True
   )
   ```

### Alternative: Use Hugging Face Models
For cloud deployment without OpenAI API, you can use Hugging Face models:

```python
# In enhanced_agent/src/dspy_mcp_integration.py
# Add support for Hugging Face models
elif "huggingface" in model_name.lower() or "hf" in model_name.lower():
    model_path = f"huggingface/{model_name}"
```

## 🔧 Troubleshooting

### Common Issues
1. **ModuleNotFoundError**: Make sure all dependencies are in `requirements.txt`
2. **Import errors**: Check that all file paths are correct
3. **API key errors**: Ensure secrets are properly configured

### Debug Mode
To debug issues, add this to your Streamlit app:
```python
import streamlit as st
st.write("Debug info:", sys.path)
st.write("Available modules:", [m for m in sys.modules.keys() if 'dspy' in m])
```

## 📝 Files Modified for Cloud Deployment
- `requirements.txt` - Added all necessary dependencies
- `.streamlit/secrets.toml` - Configuration template
- `enhanced_agent_streamlit.py` - Added graceful error handling
- `enhanced_agent/src/app.py` - Added graceful error handling
- `enhanced_agent/src/dspy_mcp_integration.py` - Added graceful error handling

## 🎯 Expected Behavior in Cloud
- ✅ App loads without errors
- ✅ Basic MCP functionality works
- ⚠️ DSPy structured reasoning may be limited without proper API keys
- ✅ Langfuse tracing works (if API keys provided)
- ✅ Streamlit UI works perfectly

## 🔄 Local vs Cloud
- **Local**: Full functionality with Ollama + gemma2:2b
- **Cloud**: Limited functionality, requires API keys for full DSPy features
