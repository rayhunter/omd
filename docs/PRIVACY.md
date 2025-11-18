# Privacy & Session Isolation

Complete guide to privacy features and session isolation in the OMD Enhanced Research Agent.

## Overview

The OMD agent includes comprehensive privacy and session isolation features:

- **Redacted Logging**: Automatic redaction of sensitive user inputs and API keys in logs
- **Session Isolation**: Per-session conversation history with automatic cleanup
- **Configurable Retention**: Control how long data is kept and when it's cleared
- **Pattern Detection**: Automatic detection and redaction of API keys, tokens, etc.

## Configuration

### Privacy Settings

Add to `config/config.development.toml`:

```toml
[privacy]
# Logging privacy
redact_user_input = true        # Redact user prompts in logs
redact_agent_output = false     # Redact agent responses in logs
redact_mcp_queries = true        # Redact MCP query content in logs

# Session isolation
enable_session_isolation = true  # Enable per-session history
session_timeout_seconds = 3600   # 1 hour timeout
auto_clear_on_logout = true      # Clear data on logout

# Data retention
max_history_messages = 50        # Max messages per session
clear_history_on_timeout = true  # Clear on timeout

# Redaction settings
redaction_placeholder = "[REDACTED]"
show_length_hint = true          # Show character count for redacted content
```

### Environment Variables

Or use environment variables:

```bash
# Privacy settings
PRIVACY_REDACT_USER_INPUT=true
PRIVACY_SESSION_TIMEOUT_SECONDS=3600
PRIVACY_MAX_HISTORY_MESSAGES=50
```

## Usage

### Redacted Logging

```python
from privacy import get_redacted_logger

logger = get_redacted_logger(__name__)

# Automatically redacts based on config
logger.info_user_input("Processing query", user_query)
logger.info_agent_output("Generated response", agent_response)
logger.info_mcp_query("Searching MCP", mcp_query)

# Always redacts API keys/tokens even if redaction is disabled
logger.info(f"API call result: {api_response}")  # Auto-redacts keys
```

### Session Management

```python
from privacy import get_session_manager

manager = get_session_manager()

# Create a session
manager.create_session("session-123", user_id="user-456")

# Add messages
manager.add_message("session-123", "user", "Hello")
manager.add_message("session-123", "assistant", "Hi there!")

# Get messages
messages = manager.get_messages("session-123", max_messages=10)

# End session (clears data if configured)
manager.end_session("session-123")
```

### Streamlit Integration

The Streamlit app automatically uses session isolation:

```python
# Session created on first interaction
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"streamlit-{uuid.uuid4().hex[:8]}"
    session_manager.create_session(
        st.session_state.session_id,
        user_id=st.session_state.get('user_id')
    )

# Messages stored per-session
session_manager.add_message(
    st.session_state.session_id,
    "user",
    user_input
)

# Auto-cleanup on logout button
if st.sidebar.button("🚪 Logout"):
    session_manager.end_session(st.session_state.session_id)
    st.session_state.clear()
    st.rerun()
```

### Agent Integration

The EnhancedResearchAgent supports session-scoped conversation history:

```python
from enhanced_agent.src.app import create_agent, run_enhanced_agent
from privacy import get_session_manager

session_manager = get_session_manager()

# Create agent with session ID for isolated history
session_id = "user-session-123"
agent = create_agent(session_id=session_id)

# Process queries - conversation history is per-session
result = await run_enhanced_agent(
    "What is Python?", 
    agent=agent, 
    session_id=session_id
)

# Get session-specific history
history = agent.get_session_history()

# Check isolation status
if agent.use_session_isolation:
    print(f"Agent using session: {agent.session_id}")
```

**Benefits:**
- Multi-user support with isolated conversations
- Automatic cleanup on logout or timeout
- Per-session history limits prevent unbounded growth
- Easy testing with multiple isolated sessions

**Integration with DSPy and MCP:**

```python
from privacy import get_redacted_logger

privacy_logger = get_redacted_logger(__name__)

# Privacy-aware logging in DSPy+MCP pipeline
privacy_logger.info_user_input("Starting research", user_query)
privacy_logger.info_mcp_query("Searching MCP", search_term)
privacy_logger.info_agent_output("Complete", result)
```

## Features

### Automatic Redaction Patterns

The logger automatically detects and redacts:

- OpenAI API keys: `sk-...`
- Langfuse keys: `pk-lf-...`, `sk-lf-...`
- GitHub tokens: `ghp_...`
- AWS keys: `AKIA...`
- Bearer tokens

### Session Timeout

Sessions automatically expire after `session_timeout_seconds` (default: 1 hour).
A background cleanup thread removes expired sessions every 5 minutes.

### History Limits

Sessions enforce `max_history_messages` limit (default: 50).
Older messages are automatically trimmed when the limit is reached.

### Isolation

Each session has its own:
- Message history
- Created/accessed timestamps
- User ID
- Custom metadata

Sessions are completely isolated from each other.

## Privacy Best Practices

### Development

```toml
[privacy]
redact_user_input = false   # See full queries for debugging
redact_agent_output = false
session_timeout_seconds = 7200  # 2 hours for dev
```

### Production

```toml
[privacy]
redact_user_input = true    # Protect user privacy
redact_agent_output = false  # Log responses for monitoring
redact_mcp_queries = true
session_timeout_seconds = 1800  # 30 minutes
auto_clear_on_logout = true
clear_history_on_timeout = true
```

### Compliance

For GDPR/CCPA compliance:
- Enable `auto_clear_on_logout`
- Enable `clear_history_on_timeout`
- Set `max_history_messages` to reasonable limit
- Enable `redact_user_input` for PII protection
- Implement user data export/deletion APIs

## API Reference

### RedactedLogger

```python
logger = get_redacted_logger(__name__)

# Privacy-aware methods
logger.info_user_input(message, content)    # Respects redact_user_input
logger.debug_user_input(message, content)
logger.info_agent_output(message, content)  # Respects redact_agent_output
logger.info_mcp_query(message, query)       # Respects redact_mcp_queries

# Standard logging (no redaction)
logger.info(message)
logger.debug(message)
logger.warning(message)
logger.error(message)
```

### SessionManager

```python
manager = get_session_manager()

# Session lifecycle
manager.create_session(session_id, user_id=None, metadata=None)
manager.get_session(session_id)
manager.end_session(session_id, clear_data=True)

# Message management
manager.add_message(session_id, role, content)
manager.get_messages(session_id, max_messages=None)
manager.clear_session_messages(session_id)

# Info
manager.get_active_sessions()
manager.get_session_count()

# Cleanup
manager.shutdown()
```

### SessionData

```python
session = manager.get_session(session_id)

session.session_id         # Session identifier
session.user_id            # User identifier
session.messages           # List of message dicts
session.created_at         # Creation timestamp
session.last_accessed      # Last activity timestamp
session.metadata           # Custom metadata dict

session.touch()            # Update last_accessed
session.is_expired(timeout)  # Check if expired
session.add_message(role, content)
session.get_messages(max_messages=None)
session.clear_messages()
```

## Monitoring

### Check Active Sessions

```python
from privacy import get_session_manager

manager = get_session_manager()
print(f"Active sessions: {len(manager.get_active_sessions())}")
print(f"Total sessions: {manager.get_session_count()}")
```

### Log Audit

With redaction enabled, logs look like:

```
2025-01-18 10:30:45 - INFO - Processing query: [REDACTED] (142 chars)
2025-01-18 10:30:46 - INFO - MCP query: [REDACTED] (87 chars)
2025-01-18 10:30:47 - INFO - Generated response: [REDACTED] (523 chars)
```

With redaction disabled but pattern detection:

```
2025-01-18 10:30:45 - INFO - API call: Bearer [REDACTED_TOKEN]
2025-01-18 10:30:46 - INFO - Using key: [REDACTED_API_KEY]
```

## Troubleshooting

### Sessions Not Isolating

**Problem**: Messages appearing across sessions

**Solution**: Ensure `enable_session_isolation = true` and session IDs are unique

### Logs Still Showing Sensitive Data

**Problem**: User input visible in logs

**Solution**: Check `redact_user_input = true` in config and restart app

### Sessions Not Expiring

**Problem**: Old sessions remain active

**Solution**: Verify `clear_history_on_timeout = true` and wait for cleanup cycle (5 min)

### Memory Growing

**Problem**: Too many sessions in memory

**Solution**: Lower `session_timeout_seconds` or `max_history_messages`

## Related Documentation

- [Configuration Guide](../config/README.md)
- [Observability Guide](OBSERVABILITY.md)
- [Security Best Practices](../SECURITY.md)
