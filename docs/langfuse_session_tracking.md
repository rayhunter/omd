# Langfuse Session Tracking Guide

## Overview

Session tracking in Langfuse allows you to group multiple traces together to see a complete conversation or user interaction flow. This is essential for:
- 📊 Tracking multi-turn conversations
- 👥 Understanding user journeys
- 🔍 Debugging user-specific issues
- 📈 Analyzing conversation patterns

## Quick Start

### 1. Set a Session

```python
from langfuse_integration import langfuse_manager

# At the start of a user session (e.g., when Streamlit session starts)
session_id = "session-123"
user_id = "user-456"  # Optional but recommended

langfuse_manager.set_session(session_id, user_id=user_id)
```

### 2. All Traces Automatically Tagged

Once a session is set, **all traces** will automatically include the session_id:

```python
# This trace will be part of the session
with langfuse_manager.trace_span("user_query"):
    # Your code here
    pass

# So will this one
langfuse_manager.trace_agent_step(
    step_type="think",
    input_data="user input",
    output_data="agent thought"
)

# And this one
langfuse_manager.trace_mcp_call(
    server_name="llama-mcp",
    query="search query",
    response="search results"
)
```

### 3. Clear Session When Done

```python
# At the end of a session (e.g., user closes tab)
langfuse_manager.clear_session()
```

## Streamlit Integration

### Using with Streamlit Session State

```python
import streamlit as st
import uuid
from langfuse_integration import langfuse_manager

# Initialize session ID in Streamlit session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"streamlit-{uuid.uuid4().hex[:8]}"
    
    # Optional: Get user ID from authentication
    st.session_state.user_id = st.experimental_user.get("id", "anonymous")
    
    # Set the Langfuse session
    langfuse_manager.set_session(
        st.session_state.session_id,
        user_id=st.session_state.user_id
    )

# Now all traces in this Streamlit session will be grouped
def process_user_query(query):
    with langfuse_manager.trace_span("streamlit_query"):
        # Process query - automatically tagged with session
        result = your_agent.process(query)
        return result
```

### Example: Chat Application

```python
import streamlit as st
from langfuse_integration import langfuse_manager

# Initialize session on first run
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.session_id = f"chat-{uuid.uuid4().hex[:8]}"
    langfuse_manager.set_session(st.session_state.session_id)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Process with automatic session tracking
    with langfuse_manager.trace_span("chat_message", 
                                      metadata={"message_count": len(st.session_state.messages)}):
        response = your_agent.process(prompt)
    
    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})
```

## Viewing Sessions in Langfuse

1. **Go to your Langfuse dashboard**: https://us.cloud.langfuse.com
2. **Click "Sessions" in the sidebar**
3. **Search for your session ID**
4. **View the session replay** showing:
   - All traces in chronological order
   - Complete conversation flow
   - Individual trace details
   - Timing information
   - User attribution

## API Reference

### `set_session(session_id, user_id=None)`
Set the current session for trace grouping.

**Parameters:**
- `session_id` (str): Unique identifier for this session
- `user_id` (str, optional): User identifier

**Example:**
```python
langfuse_manager.set_session("session-abc123", user_id="user-xyz")
```

### `set_user(user_id)`
Set just the user ID without changing session.

**Parameters:**
- `user_id` (str): User identifier

**Example:**
```python
langfuse_manager.set_user("user-xyz")
```

### `clear_session()`
Clear the current session and user IDs.

**Example:**
```python
langfuse_manager.clear_session()
```

### Properties

#### `current_session_id`
Get the currently active session ID.

```python
session = langfuse_manager.current_session_id
print(f"Current session: {session}")
```

#### `current_user_id`
Get the currently active user ID.

```python
user = langfuse_manager.current_user_id
print(f"Current user: {user}")
```

## Best Practices

### 1. Generate Unique Session IDs
```python
import uuid

# Good: Unique per session
session_id = f"chat-{uuid.uuid4().hex[:8]}"

# Bad: Same for everyone
session_id = "session-1"
```

### 2. Include Meaningful Prefixes
```python
# Different session types
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

# ❌ Bad: Set after some operations
do_stuff()  # These traces won't have session_id
langfuse_manager.set_session(session_id)
```

### 4. Always Include User ID When Available
```python
# ✅ Good: Include user context
langfuse_manager.set_session(session_id, user_id=authenticated_user_id)

# ⚠️  Okay: Anonymous sessions
langfuse_manager.set_session(session_id, user_id="anonymous")

# ❌ Avoid: Missing user attribution
langfuse_manager.set_session(session_id)  # No user_id
```

### 5. Clean Up on Session End
```python
# When user explicitly logs out or closes
def on_session_end():
    langfuse_manager.clear_session()
    # Other cleanup...
```

## Troubleshooting

### Sessions Not Grouping
- Ensure `set_session()` is called **before** creating traces
- Check that session_id is consistent across traces
- Verify session_id is being passed correctly

### Missing Traces in Session
- Traces created before `set_session()` won't be included
- Check for errors in trace creation
- Verify Langfuse is enabled

### Duplicate Sessions
- Each unique session_id creates a new session
- Reusing session_ids across different users will mix their traces
- Use unique IDs per session

## Testing

Run the session tracking test:
```bash
python test_session_tracking.py
```

This will create test sessions and show you how they appear in Langfuse.

## Additional Resources

- [Langfuse Sessions Documentation](https://langfuse.com/docs/observability/features/sessions)
- [Langfuse Python SDK](https://langfuse.com/docs/sdk/python)
- [Streamlit Session State](https://docs.streamlit.io/library/api-reference/session-state)
