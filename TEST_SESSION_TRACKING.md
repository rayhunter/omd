# Testing Session Tracking in Streamlit

## 🎯 What to Test

Your Streamlit app now has **full Langfuse session tracking** integrated! Here's what you should see and test:

## 🚀 How to Run

```bash
# Option 1: Using the run script
./run_streamlit.sh

# Option 2: Direct command
source virtual/bin/activate
streamlit run enhanced_agent_streamlit.py
```

The app will open in your browser at: http://localhost:8501

## 📊 What's Been Added

### 1. Session Initialization
- Every Streamlit session gets a unique `session_id`
- Format: `streamlit-<8-char-uuid>`
- Automatically set when you first load the page

### 2. Langfuse Status Panel (Sidebar)
Look for the **"📊 Observability (Langfuse)"** expander in the sidebar:
- ✅ Shows tracing status
- 🎯 Displays your current session ID
- 👤 Shows user ID
- 📈 Counts messages tracked
- 🔗 Link to view dashboard

### 3. Automatic Trace Grouping
All operations in your Streamlit session are automatically grouped:
- Every chat message
- Every agent query
- Every MCP server call
- All DSPy reasoning steps

## ✅ Testing Checklist

### Test 1: Single Session
1. ✅ **Open the Streamlit app**
2. ✅ **Check sidebar** - Find the "Observability" section
3. ✅ **Note the session ID** (e.g., `streamlit-a1b2c3d4`)
4. ✅ **Send 2-3 queries** through the chat
5. ✅ **Go to Langfuse dashboard**: https://us.cloud.langfuse.com
6. ✅ **Click "Sessions" in sidebar**
7. ✅ **Search for your session ID**
8. ✅ **Verify** all your queries are grouped together

### Test 2: Message Counter
1. ✅ **Check the message counter** in the Langfuse panel
2. ✅ **Send a message** - counter should increment
3. ✅ **Send another** - counter increments again
4. ✅ **Verify** the metadata in Langfuse includes message numbers

### Test 3: Multiple Sessions
1. ✅ **Open app in browser #1** - Note session ID
2. ✅ **Open app in browser #2** (incognito/different browser) - Note different session ID
3. ✅ **Send query in browser #1**
4. ✅ **Send query in browser #2**
5. ✅ **Check Langfuse** - Should see 2 separate sessions

### Test 4: Session Persistence
1. ✅ **Send a query**
2. ✅ **Refresh the page** (not hard refresh)
3. ✅ **Session ID should change** (new session)
4. ✅ **Old session still visible** in Langfuse

### Test 5: Trace Details
In Langfuse, each trace should include:
- ✅ Session ID
- ✅ User ID
- ✅ Message number
- ✅ Query length
- ✅ Tags: `streamlit`, `chat`, `user_query`
- ✅ Nested spans (DSPy, MCP calls)

## 🔍 What to Look for in Langfuse

### Sessions View
1. Go to https://us.cloud.langfuse.com
2. Click **"Sessions"** in left sidebar
3. You should see your session(s)
4. Click on a session to see:
   - **Timeline view** of all interactions
   - **Conversation replay**
   - **Individual trace details**
   - **Total time spent**
   - **User attribution**

### Trace View
Each message should create traces with:
- **Name**: `streamlit_chat_query`
- **Metadata**: Message number, query length
- **Tags**: streamlit, chat, user_query
- **Nested operations**: 
  - `dspy_mcp_research_pipeline`
  - `dspy_query_analysis`
  - `agent_step_*`
  - `mcp_call_*`

## 🐛 Troubleshooting

### Session ID Not Showing
- Check that Langfuse is enabled in `.env`
- Verify the Observability panel in sidebar
- Look for console errors in browser dev tools

### Traces Not Grouping
- Ensure session ID is set **before** processing queries
- Check that the session ID is consistent in the sidebar
- Verify Langfuse keys are correct

### Multiple Sessions for Same Browser
- This is expected behavior when you refresh
- Each page load = new Streamlit session = new Langfuse session
- Previous sessions are still saved in Langfuse

### No Traces Appearing
- Check `.env` has correct Langfuse keys
- Verify LANGFUSE_HOST is set to `https://us.cloud.langfuse.com`
- Look for errors in Streamlit console output

## 📈 Expected Results

After testing, you should see in Langfuse:

### Sessions Tab
```
streamlit-abc123de | user: streamlit-user | 3 traces | 5m ago
streamlit-xyz789fg | user: streamlit-user | 1 trace  | 2m ago
```

### Session Detail View
```
Timeline:
├─ streamlit_chat_query (2s)
│  ├─ dspy_mcp_research_pipeline (1.8s)
│  │  ├─ dspy_query_analysis (200ms)
│  │  ├─ mcp_call_llama-mcp (800ms)
│  │  └─ agent_step_synthesize (500ms)
│  
├─ streamlit_chat_query (3s)
│  └─ [nested operations...]
```

## 🎉 Success Criteria

Your session tracking is working if:
- ✅ Session ID visible in sidebar
- ✅ Message counter increments
- ✅ All traces in Langfuse have session_id
- ✅ Can view complete conversation in Sessions tab
- ✅ Multiple browser sessions stay separate
- ✅ Timeline shows chronological order

## 🔗 Next Steps

Once session tracking is verified:
1. **Try different query types** to see varied traces
2. **Test with longer conversations** (5+ messages)
3. **Experiment with MCP server selection**
4. **Check cost tracking** in Langfuse (if available)
5. **Set up alerts** for errors or slow queries

## 📝 Notes

- Session IDs are prefixed with `streamlit-` to identify source
- User ID defaults to `streamlit-user` (can be customized with auth)
- Sessions persist in Langfuse even after browser close
- You can filter by session_id, user_id, or tags in Langfuse

## 💡 Tips

- **Copy session ID** from sidebar to quickly find it in Langfuse
- **Use tags** to filter specific types of interactions
- **Session replay** is great for debugging user issues
- **Export session data** for analysis or reporting
