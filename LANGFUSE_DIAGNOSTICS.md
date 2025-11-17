# Langfuse Integration Diagnostics

## ✅ Current Status

Your Langfuse integration is **working correctly** locally. The test just sent data successfully to:
- **Dashboard URL**: https://us.cloud.langfuse.com
- **Project**: Using keys for project with public key: `pk-lf-83c77e0b-a018-4f6e-9b73-9b45f7d171d2`

## 🔍 Why You Might Not See Data in Dashboard

### 1. Check You're Looking at the Right Project

In your Langfuse dashboard:
1. Go to https://us.cloud.langfuse.com
2. Check the **project selector** (usually top-left or top-right)
3. Make sure you're viewing the project with public key ending in `...171d2`
4. Your comment in .env says: `# * Using praisonai project settings *`
   - Make sure you're viewing the **praisonai** project

### 2. Verify Recent Test Data

Search for this session in your dashboard:
- **Session ID**: `test-session-1762491224`
- **User ID**: `test-user`
- **Trace name**: `test_trace_verification`

This was just sent, so it should appear within 10-30 seconds.

### 3. Check Streamlit Cloud Deployment (If Applicable)

If you deployed to Streamlit Cloud, Langfuse will **NOT work** unless you configure secrets:

**In Streamlit Cloud Dashboard:**
1. Go to your app's settings
2. Click "Advanced settings"
3. Go to "Secrets" section
4. Add the following:

```toml
# Langfuse Configuration
LANGFUSE_PUBLIC_KEY = "pk-lf-83c77e0b-a018-4f6e-9b73-9b45f7d171d2"
LANGFUSE_SECRET_KEY = "sk-lf-523695ab-9c16-4b36-9545-46678fb5e486"
LANGFUSE_HOST = "https://us.cloud.langfuse.com"
```

4. Click "Save"
5. Reboot your app

### 4. Verify You've Actually Used the App

Langfuse only tracks data when:
- You submit queries through the Streamlit interface
- The app processes those queries
- The integration is enabled

**To generate test data:**
1. Run locally: `./run_streamlit.sh`
2. Submit a query in the chat interface
3. Check the sidebar for "📊 Observability (Langfuse)" - it should show:
   - ✅ Langfuse Tracing: ENABLED
   - Session ID
   - User ID
   - Message count

### 5. Check for Initialization Errors

Look at your Streamlit console output when the app starts. You should see:
```
✅ Langfuse initialized: https://us.cloud.langfuse.com
```

If you see warnings like:
- ⚠️ Langfuse keys not configured
- ⚠️ Langfuse integration not available
- ❌ Failed to initialize Langfuse

Then check your .env file or Streamlit secrets.

## 🧪 Quick Diagnostic Tests

### Test 1: Verify Local Integration
```bash
python3 test_langfuse_send.py
```
Expected: ✅ Test complete message with session ID

### Test 2: Check Current Configuration
```bash
python3 -c "
from langfuse_integration import langfuse_manager
print(f'Enabled: {langfuse_manager.enabled}')
print(f'Client: {langfuse_manager.client is not None}')
"
```
Expected: Both should be True

### Test 3: Run Streamlit Locally with Langfuse
```bash
./run_streamlit.sh
```
Then:
1. Submit a query
2. Check sidebar for Langfuse status
3. Note the Session ID
4. Search for that Session ID in your dashboard

## 📊 Dashboard Navigation Tips

### Finding Your Traces
1. **Traces Tab**: Main view of all traces
2. **Sessions Tab**: Group traces by session (search by session ID)
3. **Users Tab**: Group by user ID
4. **Search**: Use the search bar to find specific session IDs

### Filtering
- Filter by **Tags**: Look for `streamlit`, `chat`, `user_query`
- Filter by **Name**: Look for `streamlit_chat_query`
- Filter by **Date**: If testing now, filter to "Last hour"

### What You Should See (Per Query)
Each Streamlit query should create:
- 1 trace named `streamlit_chat_query`
- Metadata: `message_number`, `query_length`
- Tags: `streamlit`, `chat`, `user_query`
- Session ID in format: `streamlit-xxxxxxxx`

## 🚨 Common Issues

### Issue: "No traces found"
**Solutions:**
1. Wait 30 seconds after sending a query
2. Refresh the dashboard page
3. Check project selector
4. Verify time range filter (expand to "Last 24 hours")

### Issue: "Langfuse disabled via configuration"
**Solution:** Check if `LANGFUSE_ENABLED` is set to `false` in your .env

### Issue: Data in local but not in cloud deployment
**Solution:** Configure Streamlit Cloud secrets (see section 3 above)

## 🔗 Resources

- **Your Dashboard**: https://us.cloud.langfuse.com
- **Langfuse Docs**: https://langfuse.com/docs
- **Integration Code**: `langfuse_integration.py`
- **Streamlit App**: `enhanced_agent_streamlit.py` (lines 391-418, 586-594)

## 📝 Next Steps

1. ✅ Verify test data appears (session: test-session-1762491224)
2. Run Streamlit locally and submit a real query
3. Find that query's session ID in the sidebar
4. Search for that session in Langfuse dashboard
5. If deploying to cloud, configure secrets before expecting data
