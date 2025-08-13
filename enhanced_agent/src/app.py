import asyncio
from typing import Optional
import sys
from pathlib import Path
import os

# Import our integration modules
from .dspy_mcp_integration import DSPyMCPIntegration
from .mcp_client import MCPClient

# Import OpenManus components
from OpenManus.app.agent import ReActAgent
from OpenManus.app.config import Config
from OpenManus.app.schema import Message

# Configure OpenManus - Config is a singleton that auto-loads
config = Config()

# Initialize DSPy+MCP integration
try:
    dspy_mcp = DSPyMCPIntegration(
        llm_model="gpt-3.5-turbo",  # Can be configured via environment
        dspy_cache=True
    )
    print("✅ DSPy+MCP integration initialized successfully")
except Exception as e:
    print(f"⚠️  Warning: DSPy+MCP integration failed to initialize: {e}")
    print("📝 Falling back to basic MCP client")
    dspy_mcp = None
    mcp_client = MCPClient()

class EnhancedResearchAgent(ReActAgent):
    """
    An agent that combines OpenManus ReAct pattern with DSPy structured reasoning 
    and MCP information gathering for enhanced research capabilities.
    """
    
    def __init__(self, name: str, description: Optional[str] = None):
        super().__init__(name=name, description=description)
        
        # Choose integration mode based on availability
        self.use_dspy_integration = dspy_mcp is not None
        
        if self.use_dspy_integration:
            self.dspy_mcp = dspy_mcp
            print("🧠 Agent using DSPy+MCP structured reasoning")
        else:
            self.mcp_client = MCPClient()
            print("📝 Agent using basic MCP client (DSPy unavailable)")
        
        # State management
        self.current_query = None
        self.research_result = None
        self.processing_step = None
        
    async def think(self) -> bool:
        """Enhanced thinking process using DSPy structured reasoning when available"""
        # Get the last user message
        last_user_msg = next((msg for msg in reversed(self.memory.messages) 
                            if msg.role == "user"), None)
        
        if not last_user_msg:
            return False
            
        # New query to process
        if not self.current_query:
            self.current_query = last_user_msg.content
            self.processing_step = "analyze_query"
            return True
            
        # Check if we need to process the query
        if self.processing_step == "analyze_query":
            self.processing_step = "research"
            return True
            
        # Check if research is complete
        if self.processing_step == "research" and not self.research_result:
            return True
            
        # All processing done
        return False
        
    async def act(self) -> str:
        """Enhanced action execution using DSPy+MCP pipeline or fallback"""
        
        if self.processing_step == "analyze_query":
            if self.use_dspy_integration:
                # Use DSPy for query analysis
                analysis = await self.dspy_mcp.analyze_query_structure(self.current_query)
                return f"📊 Query Analysis Complete - Topic: {analysis['main_topic']}, Type: {analysis['query_type']}"
            else:
                return f"📝 Analyzing query: {self.current_query[:100]}..."
                
        elif self.processing_step == "research":
            if self.use_dspy_integration:
                # Use full DSPy+MCP structured research pipeline
                print("🚀 Executing DSPy+MCP structured research pipeline...")
                self.research_result = await self.dspy_mcp.process_research_query(self.current_query)
                
                # Format the structured result
                formatted_response = self.dspy_mcp.format_research_result(self.research_result)
                
                # Add to memory and reset state
                self.update_memory("assistant", formatted_response)
                self._reset_state()
                
                return formatted_response
                
            else:
                # Fallback to basic MCP search
                print("🔍 Gathering information via basic MCP...")
                mcp_response = self.mcp_client.search(self.current_query)
                
                basic_response = f"""
## Research Results

**Query:** {self.current_query}

**Information Gathered:**
{mcp_response}

**Note:** This response uses basic MCP integration. For enhanced structured reasoning, please ensure DSPy is properly configured.
"""
                
                # Add to memory and reset state  
                self.update_memory("assistant", basic_response)
                self._reset_state()
                
                return basic_response
        
        return "Processing completed."
    
    def _reset_state(self):
        """Reset agent state for next query"""
        self.current_query = None
        self.research_result = None
        self.processing_step = None

# Initialize OpenManus agent
agent = EnhancedResearchAgent(
    name="enhanced_agent",
    description="Enhanced research agent with MCP integration"
)

# Main application function
async def run_enhanced_agent(user_query: str) -> str:
    """Run the enhanced agent with a user query"""
    return await agent.run(user_query)

if __name__ == "__main__":
    print("🚀 Enhanced Research Agent - OpenManus + DSPy + MCP Integration")
    
    # Show integration status
    if dspy_mcp:
        print("✅ DSPy+MCP structured reasoning: ENABLED")
        print("📊 Available MCP servers:", dspy_mcp.mcp_client.list_servers())
        print("🎯 Default MCP server:", dspy_mcp.mcp_client.default_server)
    else:
        print("⚠️  DSPy structured reasoning: DISABLED (using basic MCP)")
        try:
            print("📊 Available MCP servers:", mcp_client.list_servers())
            print("🎯 Default MCP server:", mcp_client.default_server)
        except:
            print("❌ MCP client unavailable")
    
    print("-" * 50)
    print("This agent combines:")
    print("1. 🤖 OpenManus ReAct pattern for step-by-step processing")
    print("2. 🧠 DSPy structured reasoning for query analysis and response generation")
    print("3. 🔍 MCP for real-time information gathering")
    print("4. 📊 Structured pipeline: Query Analysis → Information Gathering → Synthesis → Response")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\nEnter your request (or 'quit' to exit): ")
            if user_input.lower() in ['quit', 'exit']:
                break
                
            result = asyncio.run(run_enhanced_agent(user_input))
            print("\nEnhanced Agent Response:")
            print(result)
            
        except KeyboardInterrupt:
            print("\nGracefully shutting down...")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Try another request or 'quit' to exit") 