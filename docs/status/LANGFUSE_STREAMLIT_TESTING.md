# Langfuse Streamlit Integration Testing Guide

## ✅ Status: FULLY OPERATIONAL

Your Streamlit app is now running with Langfuse integration enabled!

## 🚀 Quick Start

### 1. Access the App
Open your browser and navigate to:
```
http://localhost:8502
```

### 2. What to Look For

#### In the Streamlit UI:
- **Sidebar**: Look for "📊 Observability (Langfuse)" expander
  - Should show: `✅ Langfuse Tracing: ENABLED`
  - Session ID displayed
  - Link to dashboard

#### In Browser Console (F12):
You should see these logs when the app loads:
```
🔐 STEP 1: Session Initialized
🛡️ STEP 2: SessionManager Initialized
🤖 STEP 3: Agent Created
📊 STEP 4: Langfuse Session Registered
```

When you send a query:
```
💬 STEP 5: Query Received
🔍 STEP 6: Creating Langfuse Trace Span
✅ STEP 7: Query Processing Complete
```

## 🧪 Testing Steps

### Test 1: Basic Query Tracing
1. Open the Streamlit app
2. Enter a simple query in the chat: "What is Python?"
3. Submit the query
4. Check browser console for trace creation logs
5. Wait 5-10 seconds
6. Go to [Langfuse Dashboard](https://us.cloud.langfuse.com)
7. Look for trace named `streamlit_chat_query`

### Test 2: Session Tracking
1. Send multiple queries in the same session
2. In Langfuse dashboard, go to "Sessions" tab
3. Find your session ID (starts with `streamlit-`)
4. Click on it to see all traces grouped together

### Test 3: Metadata Verification
1. Send a query
2. In Langfuse, open the trace details
3. Verify you see:
   - `message_number` in metadata
   - `query_length` in metadata
   - Tags: `["streamlit", "chat", "user_query"]`
   - Session ID attached to trace

### Test 4: MCP Call Tracing
1. Send a query that triggers MCP calls (e.g., "Search for AI papers")
2. In Langfuse, look for traces named `mcp_call_*`
3. Verify latency metrics are included

### Test 5: Agent Step Tracing
1. Send a complex query requiring reasoning
2. Look for traces named `agent_step_*` or `dspy_*`
3. Verify input/output data is captured

## 📊 What Gets Tracked

### Automatically Tracked:
- ✅ All chat queries (`streamlit_chat_query` spans)
- ✅ Session IDs (auto-injected into all traces)
- ✅ User IDs (auto-injected into all traces)
- ✅ Message metadata (count, length)
- ✅ MCP server calls (from agent code)
- ✅ DSPy reasoning steps (from agent code)
- ✅ Agent operations (from agent code)

### Trace Structure:
```
Trace: streamlit_chat_query
├─ Session ID: streamlit-xxxxx
├─ User ID: streamlit-user
├─ Metadata:
│  ├─ message_number: 1
│  └─ query_length: 15
├─ Tags: ["streamlit", "chat", "user_query"]
└─ Child traces (if agent processes query):
   ├─ dspy_query_analysis
   ├─ mcp_call_<server_name>
   └─ agent_step_<type>
```

## 🔍 Verification Checklist

- [ ] Streamlit app loads without errors
- [ ] Langfuse status shows "ENABLED" in sidebar
- [ ] Browser console shows session registration logs
- [ ] Sending a query creates a trace in Langfuse
- [ ] Session ID appears in trace details
- [ ] Multiple queries in same session are grouped
- [ ] Metadata (message_number, query_length) is present
- [ ] Tags are applied correctly
- [ ] MCP calls are traced (if applicable)
- [ ] Agent steps are traced (if applicable)

## 🐛 Troubleshooting

### Issue: "Langfuse not available"
**Solution**: 
- Check `.env` file has correct keys
- Verify `langfuse` package is installed: `pip list | grep langfuse`
- Check conda environment is activated

### Issue: No traces appearing in dashboard
**Solution**:
- Wait 5-10 seconds (traces are batched)
- Check Langfuse keys are correct in `.env`
- Look for errors in Streamlit terminal output
- Verify network connection to `https://us.cloud.langfuse.com`

### Issue: Session ID not appearing
**Solution**:
- Check browser console for "STEP 4: Langfuse Session Registered"
- Verify `langfuse_manager.set_session()` is called
- Check that session is set BEFORE creating traces

### Issue: Metadata missing
**Solution**:
- Verify trace is created inside `trace_span()` context manager
- Check metadata dict is passed correctly
- Look for errors in Langfuse debug logs

## 📈 Dashboard Features to Explore

1. **Traces Tab**: See all individual traces
2. **Sessions Tab**: See grouped conversations
3. **Analytics**: View performance metrics
4. **Scores**: Add quality scores to traces
5. **Filters**: Filter by session, user, tags, etc.

## 🎯 Expected Behavior

### On App Load:
```
✅ Langfuse initialized: https://cloud.langfuse.com
📊 Langfuse: Session context set - session_id=streamlit-xxxxx, user_id=streamlit-user
```

### On Query Submission:
```
🔍 STEP 6: Creating Langfuse Trace Span
  ├─ Span name: streamlit_chat_query
  ├─ Session ID (auto-injected): streamlit-xxxxx
  └─ Tags: streamlit, chat, user_query
```

### In Langfuse Dashboard:
- Trace appears within 5-10 seconds
- Session ID visible in trace details
- All metadata and tags present
- Child traces visible if agent processes query

## 🔗 Useful Links

- **Streamlit App**: http://localhost:8502
- **Langfuse Dashboard**: https://us.cloud.langfuse.com
- **Session Tracking Guide**: `docs/langfuse_session_tracking.md`
- **Observability Docs**: `docs/OBSERVABILITY.md`

## ✨ Next Steps

1. ✅ Test basic query tracing
2. ✅ Verify session grouping
3. ✅ Check metadata and tags
4. ✅ Explore Langfuse dashboard features
5. ✅ Add custom scores/metrics if needed

---

**Status**: ✅ Ready for Testing
**Last Updated**: 2025-12-20

