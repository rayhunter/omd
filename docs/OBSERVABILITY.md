# 📊 Observability Guide

Complete guide to observability, monitoring, and session tracking with Langfuse integration.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Session Tracking](#session-tracking)
- [Langfuse Dashboard](#langfuse-dashboard)
- [Streamlit Integration](#streamlit-integration)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## 🌟 Overview

The OMD Enhanced Research Agent includes comprehensive observability through Langfuse integration, providing:

- **📊 Session Tracking** - Group conversation traces together
- **👥 User Attribution** - Track individual user interactions
- **⏱️ Performance Metrics** - Analyze latency and token usage
- **💰 Cost Tracking** - Monitor API costs per session/user
- **🔍 Debug Tools** - Trace complete conversation flows
- **📈 Analytics** - Understand usage patterns and optimize performance

## 🚀 Quick Start

### 1. Configure Langfuse

Create or edit your `.env` file:

```bash
# Langfuse Configuration
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://us.cloud.langfuse.com

# Optional: OpenAI API for enhanced tracing
OPENAI_API_KEY=sk-...
```

### 2. Verify Integration

```bash
# Start the application
./run_streamlit.sh

# Check the sidebar for "📊 Observability (Langfuse)" section
# You should see your session ID and status
```

### 3. View Traces

1. Go to https://us.cloud.langfuse.com
2. Click "Sessions" in the sidebar
3. Find your session ID
4. Explore the conversation traces

## 🔄 Session Tracking

### What is Session Tracking?

Session tracking groups multiple traces together to represent a complete user conversation or interaction flow. This is essential for:

- Understanding multi-turn conversations
- Debugging user-specific issues
- Analyzing conversation patterns
- Tracking costs per user/session

### Automatic Session Creation

Sessions are automatically created when you start the Streamlit app:

```python
# In Streamlit (handled automatically)
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"streamlit-{uuid.uuid4().hex[:8]}"
    langfuse_manager.set_session(st.session_state.session_id)
```

### Manual Session Management

For programmatic usage:

```python
from langfuse_integration import langfuse_manager

# Set session at the start
session_id = "user-session-123"
user_id = "user-456"  # Optional but recommended
langfuse_manager.set_session(session_id, user_id=user_id)

# All traces now automatically tagged with session_id
with langfuse_manager.trace_span("user_query"):
    result = process_query(query)

# Clear session when done
langfuse_manager.clear_session()
```

## 🖥️ Streamlit Integration

### Session Status Display

The Streamlit app includes a real-time session status panel:

```
📊 Observability (Langfuse)
━━━━━━━━━━━━━━━━━━━━━━━
🆔 Session ID: streamlit-a1b2c3d4
💬 Messages: 5
📊 Status: ✅ Active
🔗 Dashboard: [View in Langfuse →]
```

### Features

- **Persistent Session ID** - Maintained across page interactions
- **Message Counter** - Track conversation length
- **Live Status** - Real-time connection status
- **Direct Dashboard Link** - Quick access to Langfuse

### Implementation Example

```python
import streamlit as st
import uuid
from langfuse_integration import langfuse_manager

# Initialize session
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"streamlit-{uuid.uuid4().hex[:8]}"
    st.session_state.message_count = 0
    langfuse_manager.set_session(st.session_state.session_id)

# Display status in sidebar
with st.sidebar:
    st.subheader("📊 Observability (Langfuse)")
    st.write(f"**Session ID:** `{st.session_state.session_id}`")
    st.write(f"**Messages:** {st.session_state.message_count}")

    if langfuse_manager.is_enabled():
        st.success("✅ Active")
        session_url = f"https://us.cloud.langfuse.com/sessions/{st.session_state.session_id}"
        st.link_button("View in Langfuse →", session_url)
    else:
        st.warning("⚠️ Disabled")

# Process messages with automatic tracing
if prompt := st.chat_input("Your query"):
    st.session_state.message_count += 1

    # This trace is automatically tagged with session_id
    with langfuse_manager.trace_span("chat_message",
                                      metadata={"message_num": st.session_state.message_count}):
        response = process_query(prompt)
```

## 📈 Langfuse Dashboard

### Viewing Sessions

1. **Navigate to Sessions**
   - Go to https://us.cloud.langfuse.com
   - Click "Sessions" in the left sidebar

2. **Search for Your Session**
   - Use the session ID from Streamlit
   - Filter by user ID, date range, or tags

3. **Explore Session Details**
   - Timeline view of all traces
   - Individual trace details
   - Performance metrics
   - Cost breakdown

### Dashboard Features

- **Timeline View** - Chronological order of all operations
- **Trace Details** - Input/output, metadata, timing
- **Cost Analysis** - Token usage and API costs
- **Performance Metrics** - Latency, throughput
- **User Journey** - Complete conversation flow

### Useful Filters

```
# Filter by session
session_id = "streamlit-a1b2c3d4"

# Filter by user
user_id = "user-123"

# Filter by tags
tags: ["chat", "research", "dspy"]

# Filter by date
date_range: Last 7 days
```

## 📚 API Reference

### Setting Sessions

#### `set_session(session_id, user_id=None)`

Set the current session for trace grouping.

```python
langfuse_manager.set_session("session-abc123", user_id="user-xyz")
```

**Parameters:**
- `session_id` (str): Unique identifier for this session
- `user_id` (str, optional): User identifier

#### `set_user(user_id)`

Update just the user ID without changing session.

```python
langfuse_manager.set_user("user-xyz")
```

#### `clear_session()`

Clear the current session and user IDs.

```python
langfuse_manager.clear_session()
```

### Querying Session State

#### `current_session_id`

Get the currently active session ID.

```python
session = langfuse_manager.current_session_id
print(f"Active session: {session}")
```

#### `current_user_id`

Get the currently active user ID.

```python
user = langfuse_manager.current_user_id
print(f"Current user: {user}")
```

### Tracing Operations

#### `trace_span(name, **kwargs)`

Create a traced span with automatic session tagging.

```python
with langfuse_manager.trace_span("operation_name",
                                  metadata={"key": "value"},
                                  tags=["tag1", "tag2"]) as span:
    result = do_work()
    if span:
        span.update(output=result)
```

#### `trace_agent_step(step_type, input_data, output_data)`

Trace a specific agent step.

```python
langfuse_manager.trace_agent_step(
    step_type="think",
    input_data="user query",
    output_data="agent reasoning"
)
```

#### `trace_mcp_call(server_name, query, response)`

Trace an MCP server call.

```python
langfuse_manager.trace_mcp_call(
    server_name="llama-mcp",
    query="search query",
    response="search results"
)
```

## ✅ Best Practices

### 1. Generate Unique Session IDs

```python
import uuid

# ✅ Good: Unique per session
session_id = f"chat-{uuid.uuid4().hex[:8]}"

# ❌ Bad: Same for everyone
session_id = "session-1"
```

### 2. Include Meaningful Prefixes

```python
# Different session types for better organization
chat_session = f"chat-{uuid.uuid4().hex[:8]}"
research_session = f"research-{uuid.uuid4().hex[:8]}"
admin_session = f"admin-{uuid.uuid4().hex[:8]}"
```

### 3. Set Session Early

```python
# ✅ Good: Set at the start
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    langfuse_manager.set_session(generate_session_id())

# ❌ Bad: Set after operations
do_stuff()  # These traces won't have session_id
langfuse_manager.set_session(session_id)
```

### 4. Always Include User ID When Available

```python
# ✅ Good: Include user context
langfuse_manager.set_session(session_id, user_id=authenticated_user_id)

# ⚠️ Okay: Anonymous sessions
langfuse_manager.set_session(session_id, user_id="anonymous")

# ❌ Avoid: Missing user attribution
langfuse_manager.set_session(session_id)  # No user_id
```

### 5. Add Rich Metadata

```python
with langfuse_manager.trace_span("query_processing",
    metadata={
        "query_length": len(query),
        "query_type": "factual",
        "message_number": 5,
        "model": "gpt-4",
        "temperature": 0.7
    },
    tags=["chat", "research", "important"]
) as span:
    result = process_query(query)
```

### 6. Clean Up on Session End

```python
def on_session_end():
    """Called when user logs out or closes tab."""
    langfuse_manager.clear_session()
    # Other cleanup...
```

## 🐛 Troubleshooting

### Sessions Not Grouping

**Problem:** Traces appear separately instead of grouped.

**Solutions:**
```bash
# 1. Ensure set_session() called before creating traces
langfuse_manager.set_session(session_id)  # Must be FIRST
with langfuse_manager.trace_span("operation"):
    pass

# 2. Check session_id is consistent
print(f"Session: {langfuse_manager.current_session_id}")

# 3. Verify Langfuse is enabled
print(f"Enabled: {langfuse_manager.is_enabled()}")
```

### Missing Traces in Session

**Problem:** Some traces don't appear in the session.

**Solutions:**
- Traces created before `set_session()` won't be included
- Check for errors in trace creation
- Verify Langfuse credentials are correct
- Check network connectivity

### Langfuse Not Enabled

**Problem:** Observability shows "Disabled" status.

**Solutions:**
```bash
# 1. Check environment variables
cat .env | grep LANGFUSE

# 2. Verify credentials
export LANGFUSE_PUBLIC_KEY=pk-lf-...
export LANGFUSE_SECRET_KEY=sk-lf-...
export LANGFUSE_HOST=https://us.cloud.langfuse.com

# 3. Restart application
./run_streamlit.sh
```

### Duplicate Sessions

**Problem:** Multiple sessions created for same user.

**Explanation:** This is usually intentional:
- Each browser tab = separate session
- Each page refresh = new session (unless session state persisted)
- Provides conversation isolation

**If Unintended:**
```python
# Persist session across page refreshes
if 'session_id' not in st.session_state:
    # Only create new session if doesn't exist
    st.session_state.session_id = generate_session_id()
```

### High API Costs

**Problem:** Langfuse API calls contributing to costs.

**Solutions:**
```python
# Reduce trace frequency
if should_trace(step):  # Add conditional logic
    with langfuse_manager.trace_span("operation"):
        pass

# Disable in development
if os.getenv("ENVIRONMENT") == "production":
    langfuse_manager.set_session(session_id)
```

## 🧪 Testing Observability

### Test Script

```bash
# Run session tracking tests
python test_session_tracking.py
```

### Manual Testing

```python
from langfuse_integration import langfuse_manager

# 1. Set test session
langfuse_manager.set_session("test-session-123", user_id="test-user")

# 2. Create test traces
with langfuse_manager.trace_span("test_operation"):
    print("Testing observability...")

# 3. Check in dashboard
# Go to Langfuse → Sessions → Search for "test-session-123"

# 4. Clean up
langfuse_manager.clear_session()
```

## 📊 Metrics and Analytics

### Key Metrics to Track

1. **Session Duration** - Time from first to last trace
2. **Message Count** - Number of interactions per session
3. **Token Usage** - Tokens consumed per session
4. **API Costs** - Total cost per session/user
5. **Response Time** - Latency for each operation
6. **Error Rate** - Failed operations per session

### Analyzing Usage Patterns

```
# In Langfuse Dashboard:

1. Group by user_id → See per-user activity
2. Group by session_id → See conversation patterns
3. Filter by tags → Analyze specific features
4. Time series → Track usage over time
5. Cost breakdown → Identify expensive operations
```

## 🔗 Additional Resources

- [Langfuse Documentation](https://langfuse.com/docs)
- [Langfuse Sessions Guide](https://langfuse.com/docs/observability/features/sessions)
- [Langfuse Python SDK](https://langfuse.com/docs/sdk/python)
- [Streamlit Session State](https://docs.streamlit.io/library/api-reference/session-state)

## 📝 Implementation Checklist

- [ ] Langfuse credentials configured in `.env`
- [ ] Session tracking enabled in application
- [ ] Sidebar status display implemented
- [ ] Session ID generated on startup
- [ ] All operations traced with session context
- [ ] User attribution included when available
- [ ] Dashboard access verified
- [ ] Session cleanup on logout/close
- [ ] Error handling for failed traces
- [ ] Monitoring alerts configured

---

**Questions?** Check the [main README](../README.md) or open an issue on GitHub.
