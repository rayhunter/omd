# Railway Deployment Guide

## Fixed: Streamlit Theme Error

The JavaScript error you encountered was caused by Streamlit's theme system trying to access browser APIs (`window.matchMedia`) without proper server-side configuration.

### Changes Made

1. **Updated Dockerfile** - Now creates a production-ready `.streamlit/config.toml` during build
2. **Updated railway.toml** - Added environment variables for headless mode
3. **Created config template** - `.streamlit/config.toml.example` for reference

### Deploy to Railway

1. **Commit the changes:**
   ```bash
   git add Dockerfile railway.toml .streamlit/config.toml.example RAILWAY_DEPLOY.md
   git commit -m "Fix: Add Streamlit production config for Railway deployment"
   git push
   ```

2. **Set Environment Variables in Railway Dashboard:**
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `LANGFUSE_PUBLIC_KEY` - (Optional) Langfuse public key
   - `LANGFUSE_SECRET_KEY` - (Optional) Langfuse secret key
   - `LLM_MODEL` - Model to use (default: microsoft/Phi-3-mini-4k-instruct)

3. **Railway will automatically:**
   - Build using the Dockerfile
   - Create the Streamlit config
   - Start the app in headless mode
   - Expose port 8501

### Verify Deployment

After deployment, check:
- ✅ App loads without JavaScript errors
- ✅ Theme displays correctly
- ✅ No `window.matchMedia` errors in browser console

### Troubleshooting

If you still see errors:

1. **Check Railway Logs:**
   ```bash
   railway logs
   ```

2. **Verify Environment Variables:**
   - Ensure all required keys are set in Railway Dashboard
   - Check that `STREAMLIT_SERVER_HEADLESS=true` is set

3. **Browser Console:**
   - Open DevTools (F12)
   - Check for any remaining JavaScript errors
   - Verify theme loads correctly

### Local Testing

To test the production config locally:
```bash
# Copy the example config
cp .streamlit/config.toml.example .streamlit/config.toml

# Run with production settings
streamlit run enhanced_agent_streamlit.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
```

## What Was Fixed

The error occurred because:
- Streamlit's frontend theme code tried to detect system color scheme preference
- `window.matchMedia` is a browser API not available during SSR
- Missing production configuration caused theme system to fail

The fix:
- ✅ Explicit theme configuration in `config.toml`
- ✅ Headless mode enabled for server deployment
- ✅ CORS and browser stats disabled for production
- ✅ Proper server address and port binding
