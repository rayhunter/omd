"""
Integration layer combining DSPy structured reasoning with MCP information gathering.

This module provides a seamless integration between:
- DSPy modules for structured reasoning and response generation
- MCP client for external information gathering
- OpenManus agent framework for execution coordination
"""

import asyncio
import dspy
from typing import Dict, Any, List, Optional
import os
from pathlib import Path

from .dspy_modules import StructuredResearchPipeline, QuickAnalysis, ResearchPiplineResult
from .mcp_client import MCPClient


class DSPyMCPIntegration:
    """
    Integration class that orchestrates DSPy structured reasoning with MCP information gathering.
    
    This class provides the bridge between:
    1. DSPy's structured reasoning capabilities
    2. MCP's information gathering from external sources
    3. Intelligent query optimization and multi-step research flows
    """
    
    def __init__(self, 
                 mcp_config_path: str = None,
                 llm_model: str = "gpt-3.5-turbo",
                 dspy_cache: bool = True):
        """
        Initialize the DSPy-MCP integration.
        
        Args:
            mcp_config_path: Path to MCP configuration file
            llm_model: LLM model to use for DSPy reasoning
            dspy_cache: Whether to enable DSPy caching
        """
        
        # Initialize MCP client
        if mcp_config_path is None:
            mcp_config_path = str(Path(__file__).parent.parent / "config" / "mcp.json")
        
        self.mcp_client = MCPClient(config_file=mcp_config_path)
        
        # Initialize DSPy
        self._setup_dspy(llm_model, dspy_cache)
        
        # Initialize DSPy modules
        self.research_pipeline = StructuredResearchPipeline()
        self.quick_analyzer = QuickAnalysis()
        
        # Configuration and state
        self.config = {
            'max_mcp_queries': 3,  # Maximum number of MCP queries per research session
            'enable_multi_step': True,  # Enable multi-step research
            'confidence_threshold': 0.7,  # Minimum confidence for direct answers
        }
        
    def _setup_dspy(self, model_name: str, enable_cache: bool = True):
        """Setup DSPy with the specified LLM model."""
        try:
            # Try to use OpenAI model (most common case)
            if "gpt" in model_name.lower():
                lm = dspy.OpenAI(
                    model=model_name,
                    max_tokens=1000,
                    temperature=0.1
                )
            else:
                # Fall back to a generic LLM (could be Ollama, etc.)
                lm = dspy.LM(
                    model=model_name,
                    max_tokens=1000,
                    temperature=0.1
                )
                
            dspy.settings.configure(
                lm=lm,
                cache_turn_on=enable_cache
            )
            
            print(f"✅ DSPy configured with {model_name}")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not configure DSPy with {model_name}: {e}")
            print("📝 Using default DSPy configuration")
            
    async def analyze_query_structure(self, user_query: str) -> Dict[str, Any]:
        """
        Analyze query structure using DSPy to determine research strategy.
        
        Returns structured analysis including topics, search terms, and research approach.
        """
        try:
            analysis = self.quick_analyzer(user_query=user_query)
            
            print(f"🧠 DSPy Query Analysis:")
            print(f"   Topic: {analysis['main_topic']}")
            print(f"   Type: {analysis['query_type']}")
            print(f"   Search terms: {', '.join(analysis['search_terms'])}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error in DSPy query analysis: {e}")
            # Fallback to basic analysis
            return {
                'main_topic': user_query[:50] + "..." if len(user_query) > 50 else user_query,
                'sub_topics': [user_query],
                'query_type': 'general',
                'information_needs': 'General information about the topic',
                'search_terms': [user_query]
            }
    
    async def gather_information(self, search_terms: List[str], max_queries: Optional[int] = None) -> str:
        """
        Gather information using MCP client based on DSPy-generated search terms.
        
        Args:
            search_terms: List of search terms from DSPy analysis
            max_queries: Maximum number of queries to make (defaults to config)
            
        Returns:
            Aggregated information from all MCP queries
        """
        max_queries = max_queries or self.config['max_mcp_queries']
        
        gathered_info = []
        
        # Use top search terms up to max_queries limit
        for i, term in enumerate(search_terms[:max_queries]):
            try:
                print(f"🔍 MCP Query {i+1}/{min(len(search_terms), max_queries)}: '{term}'")
                
                # Query MCP for this search term
                response = self.mcp_client.search(term)
                
                if response and "Error:" not in response:
                    gathered_info.append(f"Query: {term}\nResponse: {response}\n---")
                    print(f"   ✅ Got {len(response)} characters of information")
                else:
                    print(f"   ⚠️  Query failed or returned error: {response[:100]}...")
                    
            except Exception as e:
                print(f"   ❌ MCP query failed: {e}")
                gathered_info.append(f"Query: {term}\nError: {str(e)}\n---")
        
        # Combine all gathered information
        combined_info = "\n\n".join(gathered_info)
        
        if not combined_info.strip():
            combined_info = "No external information was successfully retrieved."
            
        print(f"📋 Gathered {len(combined_info)} characters of information from {len(gathered_info)} queries")
        
        return combined_info
    
    async def process_research_query(self, user_query: str) -> ResearchPiplineResult:
        """
        Complete research processing using DSPy + MCP integration.
        
        This method orchestrates:
        1. DSPy query analysis 
        2. MCP information gathering
        3. DSPy information synthesis
        4. DSPy response generation
        
        Args:
            user_query: The user's research question
            
        Returns:
            Complete ResearchPiplineResult with structured outputs
        """
        
        print(f"🚀 Starting DSPy+MCP research pipeline for: '{user_query[:60]}...'")
        
        # Step 1: Analyze query with DSPy
        analysis = await self.analyze_query_structure(user_query)
        
        # Step 2: Gather information via MCP based on DSPy analysis  
        external_info = await self.gather_information(analysis['search_terms'])
        
        # Step 3: Process everything through DSPy structured pipeline
        try:
            print("🧠 Processing through DSPy structured reasoning pipeline...")
            result = self.research_pipeline(
                user_query=user_query,
                external_info=external_info
            )
            
            print("✅ DSPy+MCP pipeline completed successfully")
            return result
            
        except Exception as e:
            print(f"❌ Error in DSPy pipeline: {e}")
            
            # Create a fallback result
            return ResearchPiplineResult(
                main_topic=analysis['main_topic'],
                sub_topics=analysis['sub_topics'],
                query_type=analysis['query_type'],
                information_needs=analysis['information_needs'],
                search_terms=analysis['search_terms'],
                key_insights="Analysis completed with limited DSPy processing due to error.",
                relevance_assessment="Unable to fully assess relevance.",
                gaps_identified="Processing error prevented full gap analysis.",
                synthesized_context=f"Query: {user_query}\nExternal Info: {external_info[:500]}...",
                direct_answer="I encountered an error during structured processing, but gathered some information.",
                supporting_details=external_info[:1000] + "..." if len(external_info) > 1000 else external_info,
                actionable_insights="Review the gathered information and try reformulating the query.",
                confidence_level="low - processing error occurred",
                external_info=external_info
            )
    
    def format_research_result(self, result: ResearchPiplineResult) -> str:
        """
        Format the research pipeline result into a human-readable response.
        
        Args:
            result: The structured research pipeline result
            
        Returns:
            Formatted string response for the user
        """
        
        response_parts = []
        
        # Main answer
        response_parts.append("## 🎯 Direct Answer")
        response_parts.append(result.direct_answer)
        response_parts.append("")
        
        # Key insights 
        if result.key_insights and result.key_insights != "No specific insights extracted.":
            response_parts.append("## 💡 Key Insights")
            response_parts.append(result.key_insights)
            response_parts.append("")
        
        # Supporting details
        if result.supporting_details:
            response_parts.append("## 📚 Supporting Information")  
            response_parts.append(result.supporting_details)
            response_parts.append("")
        
        # Actionable insights
        if result.actionable_insights:
            response_parts.append("## 🛠️ Next Steps")
            response_parts.append(result.actionable_insights)
            response_parts.append("")
        
        # Analysis metadata (optional, for debugging)
        response_parts.append("---")
        response_parts.append(f"**Research Analysis:** {result.query_type} query about {result.main_topic}")
        response_parts.append(f"**Confidence Level:** {result.confidence_level}")
        
        if result.gaps_identified and "no significant gaps" not in result.gaps_identified.lower():
            response_parts.append(f"**Information Gaps:** {result.gaps_identified}")
        
        return "\n".join(response_parts)
    
    def get_search_terms(self, user_query: str) -> List[str]:
        """
        Quick method to get DSPy-generated search terms without full processing.
        Useful for preview or debugging.
        """
        try:
            analysis = self.quick_analyzer(user_query=user_query)
            return analysis['search_terms']
        except Exception as e:
            print(f"Error getting search terms: {e}")
            return [user_query]  # Fallback to original query