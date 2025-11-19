import streamlit as st
import asyncio
import sys
import uuid
from pathlib import Path
import time
from typing import Dict, List, Optional
# Load environment variables from .env file (if available locally)
# Streamlit Cloud uses secrets.toml instead of .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️  python-dotenv not available, using Streamlit secrets only")
    pass

# Load Streamlit secrets (for cloud deployment)
try:
    import streamlit as st
    # Streamlit secrets are automatically available in cloud
    if hasattr(st, 'secrets') and st.secrets:
        print("✅ Streamlit secrets loaded for cloud deployment")
except Exception as e:
    print(f"⚠️  Streamlit secrets not available: {e}")

# Import configuration helper
try:
    from enhanced_agent.src.config_helper import is_cloud_environment, get_openai_api_key, get_langfuse_config
    print("✅ Configuration helper loaded")
except ImportError as e:
    print(f"⚠️  Configuration helper not available: {e}")
    # Define fallback functions
    def is_cloud_environment():
        return False
    def get_openai_api_key():
        return None
    def get_langfuse_config():
        return {}

# Import Langfuse integration for session tracking
try:
    from langfuse_integration import langfuse_manager
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    langfuse_manager = None
    print("⚠️  Langfuse integration not available")

# Import privacy features
try:
    from privacy import get_session_manager, get_redacted_logger
    PRIVACY_AVAILABLE = True
    session_manager = get_session_manager()
    logger = get_redacted_logger(__name__)
except ImportError:
    PRIVACY_AVAILABLE = False
    session_manager = None
    logger = None
    print("⚠️  Privacy features not available")

# Configure Streamlit page
st.set_page_config(
    page_title="Enhanced Research Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Warm Intelligence theme custom CSS
st.markdown("""
<style>
/* Import Manrope font from Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&display=swap');

/* Apply Manrope font globally */
html, body, [class*="css"] {
    font-family: 'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* Enhanced styling for Warm Intelligence theme */
.stApp {
    background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%);
}

/* Sidebar styling */
.css-1d391kg {
    background: linear-gradient(180deg, #fef9c3 0%, #fde68a 100%);
}

/* Input fields styling */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: #fffbeb;
    border: 2px solid #fbbf24;
    color: #292524;
    font-family: 'Manrope', sans-serif;
    border-radius: 10px;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #f59e0b;
    box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2);
}

/* Button styling */
.stButton > button {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: white;
    border: none;
    border-radius: 12px;
    font-family: 'Manrope', sans-serif;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.stButton > button:hover {
    background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(245, 158, 11, 0.4);
}

/* Chat message styling */
.stChatMessage {
    background: rgba(254, 252, 232, 0.8);
    border: 2px solid #fde68a;
    border-radius: 16px;
    backdrop-filter: blur(10px);
}

/* Expander styling */
.streamlit-expanderHeader {
    background: rgba(254, 243, 199, 0.6);
    border-radius: 10px;
    font-family: 'Manrope', sans-serif;
    font-weight: 600;
    border: 1px solid #fbbf24;
}

/* Metrics styling */
.metric-container {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(251, 191, 36, 0.15) 100%);
    border: 2px solid rgba(245, 158, 11, 0.3);
    border-radius: 16px;
    padding: 1rem;
}

/* Progress bar styling */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%);
}

/* Success/error message styling */
.stSuccess, .stError, .stWarning, .stInfo {
    border-radius: 12px;
    font-family: 'Manrope', sans-serif;
}

/* Header styling */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Manrope', sans-serif;
    font-weight: 700;
    color: #292524;
}

/* Custom animation for loading states */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.75; }
}

.thinking {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Additional warm theme enhancements */
.stMarkdown {
    color: #292524;
}

/* Sidebar text */
.css-1d391kg .stMarkdown {
    color: #78350f;
}

/* Links styling */
a {
    color: #d97706;
    text-decoration: none;
    font-weight: 600;
}

a:hover {
    color: #b45309;
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

# Import the enhanced agent
try:
    from enhanced_agent.src.app import run_enhanced_agent, create_agent, dspy_mcp
    # mcp_client might not be available if dspy_mcp is working
    try:
        from enhanced_agent.src.app import mcp_client
    except ImportError:
        mcp_client = None

    # Import the enhanced MCP client for UI features
    try:
        from enhanced_agent.src.enhanced_mcp_client import EnhancedMCPClient
        enhanced_mcp = EnhancedMCPClient()
    except ImportError:
        enhanced_mcp = None

    agent_available = True
except ImportError as e:
    st.error(f"Failed to import enhanced agent: {e}")
    agent_available = False
    dspy_mcp = None
    mcp_client = None
    enhanced_mcp = None
    create_agent = None

def display_agent_status():
    """Display the status of various agent components"""
    st.sidebar.header("🔧 Agent Status")
    
    if not agent_available:
        st.sidebar.error("❌ Agent not available")
        return
    
    # DSPy+MCP Integration Status
    if dspy_mcp:
        st.sidebar.success("✅ MCP Integration & DSPy: ENABLED")
        try:
            servers = dspy_mcp.mcp_client.list_servers()
            default_server = dspy_mcp.mcp_client.default_server
            st.sidebar.info(f"🎯 Default MCP server: {default_server}")
        except Exception as e:
            st.sidebar.warning(f"⚠️ MCP status check failed: {e}")
    else:
        st.sidebar.warning("⚠️ DSPy structured reasoning: DISABLED")
        if mcp_client:
            try:
                servers = mcp_client.list_servers()
                default_server = mcp_client.default_server
                st.sidebar.info(f"🎯 Default MCP server: {default_server}")
            except Exception as e:
                st.sidebar.error(f"❌ MCP client error: {e}")
        else:
            st.sidebar.error("❌ MCP client unavailable")

def display_mcp_servers():
    """Display available MCP servers and their capabilities"""
    st.sidebar.header("🌐 Available MCP Servers")
    
    if not enhanced_mcp:
        st.sidebar.warning("Enhanced MCP client not available")
        return None
    
    try:
        servers = enhanced_mcp.list_servers()
        server_info = {}
        
        # Create expandable sections for each server
        for server_name in servers:
            info = enhanced_mcp.get_server_info(server_name)
            if info:
                with st.sidebar.expander(f"🔧 {server_name}"):
                    st.write(f"**Type:** {info.get('type', 'unknown')}")
                    st.write(f"**Description:** {info.get('description', 'No description')}")
                    capabilities = info.get('capabilities', [])
                    if capabilities:
                        st.write(f"**Capabilities:** {', '.join(capabilities)}")
                server_info[server_name] = info
        
        return server_info
    except Exception as e:
        st.sidebar.error(f"❌ Error loading server info: {e}")
        return None

def display_server_selection():
    """Display server selection options"""
    st.sidebar.header("⚙️ Server Selection")
    
    if not enhanced_mcp:
        return None, False
    
    # Server selection mode
    selection_mode = st.sidebar.radio(
        "Selection Mode:",
        ["Auto (Smart routing)", "Manual selection", "Multi-server search"],
        help="Auto: Automatically select best servers based on query\nManual: Choose specific server\nMulti-server: Search multiple servers simultaneously"
    )
    
    selected_servers = []
    use_auto = selection_mode == "Auto (Smart routing)"
    
    if selection_mode == "Manual selection":
        servers = enhanced_mcp.list_servers()
        selected_server = st.sidebar.selectbox(
            "Choose server:",
            servers,
            help="Select a specific MCP server for your query"
        )
        selected_servers = [selected_server] if selected_server else []
        
    elif selection_mode == "Multi-server search":
        servers = enhanced_mcp.list_servers()
        selected_servers = st.sidebar.multiselect(
            "Choose servers:",
            servers,
            default=[servers[0]] if servers else [],
            help="Select multiple servers to search simultaneously"
        )
    
    return selected_servers, use_auto

def display_architecture_info():
    """Display information about the agent architecture"""
    st.sidebar.header("🏗️ Architecture")
    
    components = [
        "🤖 **OpenManus ReAct Pattern**\n   Step-by-step processing",
        "🔍 **MCP Integration**\n   Real-time information gathering",
        "🧠 **DSPy Structured Reasoning**\n   Query analysis & response generation",     
        "📊 **Processing Pipeline**\n   Query → Info Gathering → Analysis → Synthesis"
    ]
    
    for component in components:
        st.sidebar.markdown(component)

# ============================================================================
# Async Event Loop Management
# ============================================================================
# Streamlit runs synchronously, but our agent code uses async/await.
# To avoid the overhead of creating/closing event loops repeatedly,
# we store a persistent event loop in st.session_state and reuse it
# for all async operations within a session.
# ============================================================================

def get_or_create_event_loop():
    """
    Get or create a persistent event loop stored in session state.
    This ensures we reuse the same event loop across all async operations
    in the Streamlit session, avoiding the overhead of creating/closing loops.

    Returns:
        asyncio.AbstractEventLoop: The event loop for this session
    """
    if 'event_loop' not in st.session_state:
        # Create a new event loop and store it in session state
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        st.session_state.event_loop = loop
        print("🔄 Created new event loop for session")

    return st.session_state.event_loop

def run_async(coro):
    """
    Centralized async execution helper that reuses the session event loop.

    This function ensures all async operations in Streamlit use the same
    event loop, avoiding the overhead and potential issues of creating
    and destroying loops repeatedly.

    Usage:
        result = run_async(some_async_function(arg1, arg2))

    Args:
        coro: A coroutine to execute

    Returns:
        The result of the coroutine execution

    Raises:
        RuntimeError: If the event loop is already running (shouldn't happen in Streamlit)
    """
    loop = get_or_create_event_loop()

    # Check if loop is running (shouldn't be in Streamlit, but safety check)
    if loop.is_running():
        # If loop is already running, we can't use run_until_complete
        # This shouldn't happen in Streamlit's execution model
        raise RuntimeError("Event loop is already running. Use await instead.")

    # Run the coroutine on the persistent loop
    return loop.run_until_complete(coro)

def cleanup_event_loop():
    """
    Cleanup function to properly close the event loop when the session ends.
    Note: Streamlit doesn't provide a built-in session cleanup hook,
    so this needs to be called manually if needed.
    """
    if 'event_loop' in st.session_state:
        loop = st.session_state.event_loop
        if not loop.is_closed():
            # Cancel all pending tasks
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            # Close the loop
            loop.close()
            print("🔄 Event loop closed")
        del st.session_state.event_loop

async def process_query(user_input: str, agent, servers=None, use_auto=True, session_id=None):
    """
    Process user query with the enhanced agent.

    Args:
        user_input: The user's query string
        agent: The agent instance to use (from session state)
        servers: Optional list of servers to query (for future multi-server support)
        use_auto: Whether to use auto server selection (for future multi-server support)
        session_id: Optional session ID for session-aware processing

    Returns:
        Tuple of (result, error) where result is the response string and error is None,
        or (None, error_string) if an error occurred
    """
    try:
        result = await run_enhanced_agent(user_input, agent=agent, session_id=session_id)
        return result, None
    except Exception as e:
        return None, str(e)

def display_multi_server_results(results: Dict[str, str]):
    """Display results from multiple MCP servers in a nice format"""
    if not results:
        st.warning("No results from any servers")
        return
    
    st.markdown("### 🔍 Multi-Server Results")
    
    # Create tabs for each server
    if len(results) > 1:
        tabs = st.tabs([f"🔧 {server}" for server in results.keys()])
        
        for i, (server_name, result) in enumerate(results.items()):
            with tabs[i]:
                server_info = enhanced_mcp.get_server_info(server_name) if enhanced_mcp else {}
                server_type = server_info.get('type', 'unknown')
                description = server_info.get('description', 'No description')
                
                st.markdown(f"**{server_name}** ({server_type})")
                st.markdown(f"*{description}*")
                st.markdown("---")
                
                if result.startswith("Error:"):
                    st.error(result)
                else:
                    st.markdown(result)
    else:
        # Single result
        server_name, result = list(results.items())[0]
        st.markdown(f"**Results from {server_name}:**")
        if result.startswith("Error:"):
            st.error(result)
        else:
            st.markdown(result)

def test_mcp_servers(query: str, servers: List[str] = None):
    """Test multiple MCP servers with a query"""
    if not enhanced_mcp:
        st.error("Enhanced MCP client not available")
        return
    
    if not servers:
        servers = enhanced_mcp.list_servers()[:3]  # Test first 3 servers
    
    st.markdown("### 🧪 Testing MCP Servers")
    
    with st.spinner("Testing servers..."):
        results = enhanced_mcp.search(query, servers)
    
    display_multi_server_results(results)

def main():
    # Initialize session ID (shared by all features)
    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"streamlit-{uuid.uuid4().hex[:8]}"
        st.session_state.user_id = "streamlit-user"  # Could be from auth
        st.session_state.session_created_at = time.time()
        if logger:
            logger.info(f"Created new session: {st.session_state.session_id}")

        # Browser console log: Step 1 - Session initialization
        st.html(f"""
        <script>
            console.log("🔐 STEP 1: Session Initialized");
            console.log("  ├─ Session ID: {st.session_state.session_id}");
            console.log("  ├─ User ID: {st.session_state.user_id}");
            console.log("  └─ Timestamp: {time.time()}");
        </script>
        """)
    
    # Initialize SessionManager
    if PRIVACY_AVAILABLE and session_manager:
        if 'privacy_session_initialized' not in st.session_state:
            session_manager.create_session(
                st.session_state.session_id,
                user_id=st.session_state.user_id
            )
            st.session_state.privacy_session_initialized = True
            if logger:
                logger.info("SessionManager initialized for session")

            # Browser console log: Step 2 - SessionManager initialization
            st.html(f"""
            <script>
                console.log("🛡️ STEP 2: SessionManager Initialized");
                console.log("  ├─ Session ID: {st.session_state.session_id}");
                console.log("  ├─ Privacy features: ENABLED");
                console.log("  └─ Isolation mode: ACTIVE");
            </script>
            """)
    
    # Initialize session-scoped agent instance
    if "agent" not in st.session_state and agent_available and create_agent:
        # Pass session_id to create session-aware agent
        st.session_state.agent = create_agent(session_id=st.session_state.session_id)
        if logger:
            logger.info(f"Created session-aware agent instance: {st.session_state.session_id}")

        # Browser console log: Step 3 - Agent initialization
        st.html(f"""
        <script>
            console.log("🤖 STEP 3: Agent Created");
            console.log("  ├─ Session ID: {st.session_state.session_id}");
            console.log("  ├─ Agent type: EnhancedResearchAgent");
            console.log("  └─ Session-aware: TRUE");
        </script>
        """)

    # Initialize Langfuse session tracking
    if LANGFUSE_AVAILABLE and langfuse_manager.enabled:
        if 'langfuse_session_id' not in st.session_state:
            st.session_state.langfuse_session_id = st.session_state.session_id
            st.session_state.langfuse_user_id = st.session_state.user_id

            # Set the session in Langfuse
            langfuse_manager.set_session(
                st.session_state.langfuse_session_id,
                user_id=st.session_state.langfuse_user_id
            )

            # Browser console log: Step 4 - Langfuse registration
            st.html(f"""
            <script>
                console.log("📊 STEP 4: Langfuse Session Registered");
                console.log("  ├─ Langfuse Session ID: {st.session_state.langfuse_session_id}");
                console.log("  ├─ Langfuse User ID: {st.session_state.langfuse_user_id}");
                console.log("  ├─ Observability: ENABLED");
                console.log("  └─ Auto-tagging: ALL TRACES");
            </script>
            """)
    
    # Header
    st.title("🧠 Enhanced Research Agent")
    st.markdown("*Powered by OpenManus + MCP Integration + DSPy*")
    
    # Display session info and logout button
    with st.sidebar:
        st.markdown("### 🔐 Session Info")
        st.caption(f"Session: `{st.session_state.session_id[:8]}...`")
        
        if PRIVACY_AVAILABLE and session_manager:
            session_data = session_manager.get_session(st.session_state.session_id)
            if session_data:
                msg_count = len(session_data.messages)
                st.caption(f"Messages: {msg_count}/{session_manager.config.max_history_messages}")
                
                # Session age
                age_minutes = int((time.time() - st.session_state.session_created_at) / 60)
                timeout_minutes = int(session_manager.config.session_timeout_seconds / 60)
                st.caption(f"Age: {age_minutes}m / {timeout_minutes}m timeout")
        
        # Logout button
        if st.button("🚪 Logout & Clear Session", use_container_width=True):
            old_session_id = st.session_state.session_id

            # Browser console log: Session cleanup
            st.html(f"""
            <script>
                console.log("🚪 STEP 8: Session Cleanup");
                console.log("  ├─ Ending session: {old_session_id}");
                console.log("  ├─ Clearing SessionManager data");
                console.log("  ├─ Clearing Langfuse session context");
                console.log("  └─ Clearing Streamlit session state");
            </script>
            """)

            if PRIVACY_AVAILABLE and session_manager:
                session_manager.end_session(st.session_state.session_id)
                if logger:
                    logger.info(f"User logged out, session cleared: {st.session_state.session_id}")

            if LANGFUSE_AVAILABLE and langfuse_manager.enabled:
                langfuse_manager.clear_session()

            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]

            st.success("Session cleared!")
            st.rerun()
        
        st.markdown("---")
    
    # Display Langfuse status
    if LANGFUSE_AVAILABLE and langfuse_manager.enabled:
        with st.sidebar.expander("📊 Observability (Langfuse)", expanded=False):
            st.success("✅ Langfuse Tracing: ENABLED")
            st.caption(f"🎯 Session: `{st.session_state.langfuse_session_id}`")
            st.caption(f"👤 User: `{st.session_state.langfuse_user_id}`")
            
            if 'message_count' in st.session_state:
                st.metric("Messages Tracked", st.session_state.message_count)
            
            st.markdown("---")
            st.caption("🔗 [View Dashboard](https://us.cloud.langfuse.com)")
    
    # Display status and info in sidebar
    display_agent_status()
    st.sidebar.markdown("---")
    display_mcp_servers()
    st.sidebar.markdown("---")
    selected_servers, use_auto = display_server_selection()
    st.sidebar.markdown("---")
    display_architecture_info()
    
    # Main interface
    if not agent_available:
        st.error("Enhanced agent is not available. Please check the installation.")
        st.stop()
    
    # Instructions
    st.markdown("""
    ### 🚀 How to use:
    1. **Choose your information sources** in the sidebar:
       - **Auto routing**: Smart selection based on your query
       - **Manual selection**: Pick a specific server  
       - **Multi-server**: Search multiple sources simultaneously
    2. Enter your research question or request below
    3. Click "Process Query" or press Ctrl+Enter
    4. The agent will analyze, gather information, and provide a structured response
    
    **Example queries by server type:**
    - **General knowledge**: "Explain quantum computing principles"
    - **Current events**: "Latest developments in AI regulation"
    - **Scientific research**: "Recent papers on climate change"
    - **Financial data**: "AAPL stock performance"
    - **Weather**: "Weather in San Francisco"
    - **Code/GitHub**: "Best Python machine learning libraries"
    """)
    
    # Add a test section
    if enhanced_mcp:
        with st.expander("🧪 Test Multiple MCP Servers"):
            st.markdown("Test how different servers respond to the same query:")
            
            test_query = st.text_input("Test query:", placeholder="Enter a test query...")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔍 Test All Available Servers"):
                    if test_query:
                        test_mcp_servers(test_query)
                    else:
                        st.warning("Please enter a test query")
            
            with col2:
                if st.button("🎯 Test Selected Servers"):
                    if test_query and selected_servers:
                        test_mcp_servers(test_query, selected_servers)
                    elif not test_query:
                        st.warning("Please enter a test query")
                    else:
                        st.warning("Please select servers in the sidebar")
    

    # Alternative form-based input with progress indicators
    st.markdown("---")

    with st.expander("📝 Detailed Research Form (Advanced)", expanded=False):
        st.caption("Use this form for longer queries with visual progress indicators and download options")

        with st.form("query_form", clear_on_submit=True):
            user_input = st.text_area(
                "Enter your research question:",
                height=100,
                placeholder="What would you like to research today?"
            )

            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                submitted = st.form_submit_button("🚀 Process Query", type="primary")

            if submitted and user_input:
                # Add to session manager
                if PRIVACY_AVAILABLE and session_manager:
                    session_manager.add_message(st.session_state.session_id, "user", user_input)
                
                # Add to chat history
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                # Log with privacy
                if logger:
                    logger.info_user_input("Processing form query", user_input)

                # Process query
                with st.spinner("🧠 Enhanced agent is thinking..."):
                    # Create progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    # Simulate processing steps
                    steps = [
                        "🔍 Analyzing query structure...",
                        "📊 Gathering information via MCP...",
                        "🧠 Processing with DSPy reasoning...",
                        "⚙️ Synthesizing response...",
                        "✅ Finalizing result..."
                    ]

                    for i, step in enumerate(steps):
                        status_text.text(step)
                        progress_bar.progress((i + 1) / len(steps))
                        time.sleep(0.5)  # Visual delay for better UX

                    # Run the actual query using centralized async helper
                    result, error = run_async(process_query(
                        user_input, 
                        agent=st.session_state.agent,
                        session_id=st.session_state.session_id
                    ))

                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()

                    if error:
                        error_msg = f"❌ **Error:** {error}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                        
                        # Add to session manager
                        if PRIVACY_AVAILABLE and session_manager:
                            session_manager.add_message(st.session_state.session_id, "assistant", error_msg)
                    else:
                        st.success("✅ **Response generated successfully!**")

                        # Display the result in a nice format
                        st.markdown("### 🎯 Enhanced Agent Response:")
                        st.markdown(result)

                        # Add to chat history
                        st.session_state.messages.append({"role": "assistant", "content": result})
                        
                        # Add to session manager
                        if PRIVACY_AVAILABLE and session_manager:
                            session_manager.add_message(st.session_state.session_id, "assistant", result)
                        
                        # Log with privacy
                        if logger:
                            logger.info_agent_output("Form query completed", result)

                        # Store the result for download outside the form
                        st.session_state.last_result = result

        # Download button outside the form
        if hasattr(st.session_state, 'last_result') and st.session_state.last_result:
            st.download_button(
                label="📄 Download Last Response",
                data=st.session_state.last_result,
                file_name=f"research_response_{int(time.time())}.md",
                mime="text/markdown",
                key="download_last_response"
            )
    
    # Chat interface
    st.markdown("---")
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.message_count = 0
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Enter your research question..."):
        # Increment message count
        st.session_state.message_count = st.session_state.get('message_count', 0) + 1

        # Browser console log: Step 5 - Query received
        st.html(f"""
        <script>
            console.log("💬 STEP 5: Query Received");
            console.log("  ├─ Session ID: {st.session_state.session_id}");
            console.log("  ├─ Message #: {st.session_state.message_count}");
            console.log("  ├─ Query length: {len(prompt)} chars");
            console.log("  └─ Will be auto-tagged with session_id in Langfuse");
        </script>
        """)

        # Add to session manager
        if PRIVACY_AVAILABLE and session_manager:
            session_manager.add_message(st.session_state.session_id, "user", prompt)

        # Log with privacy
        if logger:
            logger.info_user_input("Processing chat query", prompt)
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process the query with Langfuse tracing
        with st.chat_message("assistant"):
            with st.spinner("🧠 Processing your request..."):
                # Wrap processing in Langfuse trace if available
                if LANGFUSE_AVAILABLE and langfuse_manager.enabled:
                    # Browser console log: Step 6 - Trace span creation
                    st.html(f"""
                    <script>
                        console.log("🔍 STEP 6: Creating Langfuse Trace Span");
                        console.log("  ├─ Span name: streamlit_chat_query");
                        console.log("  ├─ Session ID (auto-injected): {st.session_state.session_id}");
                        console.log("  ├─ User ID (auto-injected): {st.session_state.user_id}");
                        console.log("  ├─ Message #: {st.session_state.message_count}");
                        console.log("  └─ Tags: streamlit, chat, user_query");
                    </script>
                    """)

                    with langfuse_manager.trace_span(
                        "streamlit_chat_query",
                        metadata={
                            "message_number": st.session_state.message_count,
                            "query_length": len(prompt)
                        },
                        tags=["streamlit", "chat", "user_query"]
                    ):
                        # Run async function using centralized helper
                        result, error = run_async(process_query(
                            prompt,
                            agent=st.session_state.agent,
                            session_id=st.session_state.session_id
                        ))
                else:
                    # Run without tracing using centralized helper
                    result, error = run_async(process_query(
                        prompt,
                        agent=st.session_state.agent,
                        session_id=st.session_state.session_id
                    ))
                
                if error:
                    error_msg = f"❌ **Error:** {error}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

                    # Add to session manager
                    if PRIVACY_AVAILABLE and session_manager:
                        session_manager.add_message(st.session_state.session_id, "assistant", error_msg)

                    # Browser console log: Error response
                    st.html(f"""
                    <script>
                        console.error("❌ STEP 7: Query Processing Error");
                        console.log("  ├─ Session ID: {st.session_state.session_id}");
                        console.log("  └─ Error logged to Langfuse with session_id");
                    </script>
                    """)
                else:
                    st.markdown(result)
                    st.session_state.messages.append({"role": "assistant", "content": result})

                    # Add to session manager
                    if PRIVACY_AVAILABLE and session_manager:
                        session_manager.add_message(st.session_state.session_id, "assistant", result)

                    # Log with privacy
                    if logger:
                        logger.info_agent_output("Chat query completed", result)

                    # Browser console log: Step 7 - Response completed
                    st.html(f"""
                    <script>
                        console.log("✅ STEP 7: Query Processing Complete");
                        console.log("  ├─ Session ID: {st.session_state.session_id}");
                        console.log("  ├─ Response length: {len(result)} chars");
                        console.log("  ├─ Trace completed in Langfuse");
                        console.log("  └─ All traces tagged with session_id: {st.session_state.session_id}");
                        console.log("");
                        console.log("🎯 Session ID Flow Summary:");
                        console.log("  Streamlit → SessionManager → Agent → Langfuse");
                        console.log("  All components use same session_id: {st.session_state.session_id}");
                    </script>
                    """)
    
   
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
    <span>&copy;2025 Conceived by LikeSugarAI, powered by OpenManus<br /></span>
    <small>Enhanced Research Agent | OMD: OpenManus + MCP Integration + DSPy</small>
    <hr />
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
