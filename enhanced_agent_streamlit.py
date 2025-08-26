import streamlit as st
import asyncio
import sys
from pathlib import Path
import time

# Configure Streamlit page
st.set_page_config(
    page_title="Enhanced Research Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import the enhanced agent
try:
    from enhanced_agent.src.app import run_enhanced_agent, dspy_mcp
    # mcp_client might not be available if dspy_mcp is working
    try:
        from enhanced_agent.src.app import mcp_client
    except ImportError:
        mcp_client = None
    agent_available = True
except ImportError as e:
    st.error(f"Failed to import enhanced agent: {e}")
    agent_available = False
    dspy_mcp = None
    mcp_client = None

def display_agent_status():
    """Display the status of various agent components"""
    st.sidebar.header("🔧 Agent Status")
    
    if not agent_available:
        st.sidebar.error("❌ Agent not available")
        return
    
    # DSPy+MCP Integration Status
    if dspy_mcp:
        st.sidebar.success("✅ DSPy+MCP Integration: ENABLED")
        try:
            servers = dspy_mcp.mcp_client.list_servers()
            default_server = dspy_mcp.mcp_client.default_server
            st.sidebar.info(f"📊 Available MCP servers: {servers}")
            st.sidebar.info(f"🎯 Default MCP server: {default_server}")
        except Exception as e:
            st.sidebar.warning(f"⚠️ MCP status check failed: {e}")
    else:
        st.sidebar.warning("⚠️ DSPy structured reasoning: DISABLED")
        if mcp_client:
            try:
                servers = mcp_client.list_servers()
                default_server = mcp_client.default_server
                st.sidebar.info(f"📊 Available MCP servers: {servers}")
                st.sidebar.info(f"🎯 Default MCP server: {default_server}")
            except Exception as e:
                st.sidebar.error(f"❌ MCP client error: {e}")
        else:
            st.sidebar.error("❌ MCP client unavailable")

def display_architecture_info():
    """Display information about the agent architecture"""
    st.sidebar.header("🏗️ Architecture")
    
    components = [
        "🤖 **OpenManus ReAct Pattern**\n   Step-by-step processing",
        "🧠 **DSPy Structured Reasoning**\n   Query analysis & response generation", 
        "🔍 **MCP Integration**\n   Real-time information gathering",
        "📊 **Processing Pipeline**\n   Query → Analysis → Info Gathering → Synthesis"
    ]
    
    for component in components:
        st.sidebar.markdown(component)

async def process_query(user_input: str):
    """Process user query with the enhanced agent"""
    try:
        result = await run_enhanced_agent(user_input)
        return result, None
    except Exception as e:
        return None, str(e)

def main():
    # Header
    st.title("🧠 Enhanced Research Agent")
    st.markdown("*Powered by OpenManus + DSPy + MCP Integration*")
    
    # Display status and info in sidebar
    display_agent_status()
    st.sidebar.markdown("---")
    display_architecture_info()
    
    # Main interface
    if not agent_available:
        st.error("Enhanced agent is not available. Please check the installation.")
        st.stop()
    
    # Instructions
    st.markdown("""
    ### 🚀 How to use:
    1. Enter your research question or request below
    2. Click "Process Query" or press Ctrl+Enter
    3. The agent will analyze, gather information, and provide a structured response
    
    **Example queries:**
    - "What are the latest developments in quantum computing?"
    - "How can small businesses benefit from AI automation?"
    - "Design a sustainable city planning strategy"
    """)
    
    # Chat interface
    st.markdown("---")
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Enter your research question..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process the query
        with st.chat_message("assistant"):
            with st.spinner("🧠 Processing your request..."):
                # Run async function in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result, error = loop.run_until_complete(process_query(prompt))
                finally:
                    loop.close()
                
                if error:
                    error_msg = f"❌ **Error:** {error}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                else:
                    st.markdown(result)
                    st.session_state.messages.append({"role": "assistant", "content": result})
    
    # Alternative form-based input (in case chat input doesn't work well)
    st.markdown("---")
    st.markdown("### 📝 Alternative Input")
    
    with st.form("query_form", clear_on_submit=True):
        user_input = st.text_area(
            "Enter your research question:", 
            height=100,
            placeholder="What would you like to research today?"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col2:
            submitted = st.form_submit_button("🚀 Process Query", type="primary")
        
        if submitted and user_input:
            # Add to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})
            
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
                
                # Run the actual query
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result, error = loop.run_until_complete(process_query(user_input))
                finally:
                    loop.close()
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                if error:
                    st.error(f"❌ **Error:** {error}")
                    st.session_state.messages.append({"role": "assistant", "content": f"❌ **Error:** {error}"})
                else:
                    st.success("✅ **Response generated successfully!**")
                    
                    # Display the result in a nice format
                    st.markdown("### 🎯 Enhanced Agent Response:")
                    st.markdown(result)
                    
                    # Add to chat history
                    st.session_state.messages.append({"role": "assistant", "content": result})
                    
                    # Option to download response
                    st.download_button(
                        label="📄 Download Response",
                        data=result,
                        file_name=f"research_response_{int(time.time())}.md",
                        mime="text/markdown"
                    )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
    <small>Enhanced Research Agent | OMD: OpenManus + MCP Integration + DSPy</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
