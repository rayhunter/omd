# Model Configuration Guide

This guide shows how to configure different language models for your Enhanced Research Agent.

## 🏠 **Local Models (Ollama)**

### Current Configuration
```python
# In enhanced_agent/src/app.py
dspy_mcp = DSPyMCPIntegration(
    llm_model="gemma2:2b",  # Your current model
    dspy_cache=True
)
```

### Alternative Local Models
```python
# Microsoft Phi-3 (if available in Ollama)
llm_model="phi3:mini"

# Llama 3.2 (if available in Ollama)  
llm_model="llama3.2:3b"

# Qwen2.5 (if available in Ollama)
llm_model="qwen2.5:1.5b"
```

## ☁️ **Cloud Models (Hugging Face)**

### For Streamlit Cloud Deployment
```python
# In enhanced_agent/src/app.py
dspy_mcp = DSPyMCPIntegration(
    llm_model="microsoft/Phi-3-mini-4k-instruct",  # Best overall
    dspy_cache=True
)
```

### Alternative Cloud Models
```python
# Direct Gemma-2 replacement
llm_model="google/gemma-2-2b-it"

# Fast coding model
llm_model="Qwen/Qwen2.5-Coder-1.5B-Instruct"

# Tiny but capable
llm_model="TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Microsoft Phi-2 (similar size to gemma2:2b)
llm_model="microsoft/phi-2"
```

## 🔄 **Easy Model Switching**

### Method 1: Environment Variable
```python
import os
model_name = os.getenv("LLM_MODEL", "gemma2:2b")  # Default to local
dspy_mcp = DSPyMCPIntegration(llm_model=model_name)
```

### Method 2: Configuration File
Create a `model_config.py`:
```python
# Local development
LOCAL_MODEL = "gemma2:2b"

# Cloud deployment  
CLOUD_MODEL = "microsoft/Phi-3-mini-4k-instruct"

# Auto-detect environment
import os
if os.getenv("STREAMLIT_CLOUD"):
    MODEL = CLOUD_MODEL
else:
    MODEL = LOCAL_MODEL
```

## 📊 **Performance Comparison**

| Model | Size | Speed | Reasoning | Code | Best For |
|-------|------|-------|-----------|------|----------|
| gemma2:2b | 2B | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Local development |
| Phi-3-mini | 3.8B | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Cloud deployment |
| Qwen2.5-Coder | 1.5B | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | Fast coding |
| TinyLlama | 1.1B | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | Quick responses |
| Phi-2 | 2.7B | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Balanced |

## 🚀 **Quick Setup for Cloud**

1. **Update your app.py**:
   ```python
   # Change this line in enhanced_agent/src/app.py
   dspy_mcp = DSPyMCPIntegration(
       llm_model="microsoft/Phi-3-mini-4k-instruct",  # For cloud
       dspy_cache=True
   )
   ```

2. **Deploy to Streamlit Cloud** - No API keys needed!

3. **Test locally** - Still works with your local gemma2:2b

## 💡 **Recommendations**

- **Local Development**: Keep `gemma2:2b` (fast, private)
- **Cloud Deployment**: Use `microsoft/Phi-3-mini-4k-instruct` (best performance)
- **Budget Conscious**: Use `TinyLlama` (fastest, smallest)
- **Code Focused**: Use `Qwen2.5-Coder` (specialized for coding)
