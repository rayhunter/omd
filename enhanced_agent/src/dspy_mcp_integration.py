"""
Integration layer combining DSPy structured reasoning with MCP information gathering.

This module provides a seamless integration between:
- DSPy modules for structured reasoning and response generation
- MCP client for external information gathering
- OpenManus agent framework for execution coordination
"""

import asyncio
import dspy
import time
from typing import Dict, Any, List, Optional
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to path for langfuse_integration
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from .dspy_modules import StructuredResearchPipeline, QuickAnalysis, ResearchPiplineResult
from .mcp_client import MCPClient

# Import Langfuse integration
try:
    from langfuse_integration import langfuse_manager
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    langfuse_manager = None
    print("⚠️  Langfuse integration not available")


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
            # Use the modern DSPy API (3.0+)
            if "gpt" in model_name.lower():
                # For OpenAI models, use the openai/ prefix
                model_path = f"openai/{model_name}"
            elif "claude" in model_name.lower():
                # For Anthropic models
                model_path = f"anthropic/{model_name}"
            elif "gemini" in model_name.lower():
                # For Google models
                model_path = f"google/{model_name}"
            else:
                # For other models (Ollama, etc.)
                model_path = model_name
            
            # Configure DSPy with the modern API
            dspy.configure(
                lm=dspy.LM(
                    model=model_path,
                    max_tokens=1000,
                    temperature=0.1
                ),
                cache_turn_on=enable_cache
            )
            
            print(f"✅ DSPy configured with {model_name} (using {model_path})")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not configure DSPy with {model_name}: {e}")
            print("📝 Using default DSPy configuration")
            
    async def analyze_query_structure(self, user_query: str) -> Dict[str, Any]:
        """
        Analyze query structure using DSPy to determine research strategy.
        
        Returns structured analysis including topics, search terms, and research approach.
        """
        # Use with statement for proper context management
        if LANGFUSE_AVAILABLE and langfuse_manager.enabled:
            with langfuse_manager.trace_span(
                "dspy_query_analysis",
                metadata={"query_length": len(user_query)},
                tags=["dspy", "analysis"]
            ) as span:
                try:
                    start_time = time.time()
                    analysis = self.quick_analyzer(user_query=user_query)
                    elapsed = (time.time() - start_time) * 1000  # ms
                    
                    print(f"🧠 DSPy Query Analysis:")
                    print(f"   Topic: {analysis['main_topic']}")
                    print(f"   Type: {analysis['query_type']}")
                    print(f"   Search terms: {', '.join(analysis['search_terms'])}")
                    
                    # Update span metadata
                    if span:
                        span.update(
                            input=user_query,
                            output=str(analysis),
                            metadata={
                                "latency_ms": elapsed,
                                "main_topic": analysis['main_topic'],
                                "query_type": analysis['query_type'],
                                "search_terms_count": len(analysis['search_terms'])
                            }
                        )
                    
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
        else:
            # No tracing - just run the analysis
            try:
                analysis = self.quick_analyzer(user_query=user_query)
                
                print(f"🧠 DSPy Query Analysis:")
                print(f"   Topic: {analysis['main_topic']}")
                print(f"   Type: {analysis['query_type']}")
                print(f"   Search terms: {', '.join(analysis['search_terms'])}")
                
                return analysis
                
            except Exception as e:
                print(f"❌ Error in DSPy query analysis: {e}")
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
        
        # Parse search terms if they come as a single string with line breaks
        if len(search_terms) == 1 and '\n' in search_terms[0]:
            # Split multi-line search terms and clean them
            parsed_terms = []
            for line in search_terms[0].split('\n'):
                line = line.strip()
                if line and not line.startswith(('#', '-', '•')):
                    # Remove numbering like "1. " or "2. "
                    if '. ' in line and line[0].isdigit():
                        line = line.split('. ', 1)[1]
                    parsed_terms.append(line)
            search_terms = parsed_terms[:max_queries]  # Limit to max_queries
        
        # Use top search terms up to max_queries limit
        for i, term in enumerate(search_terms[:max_queries]):
            try:
                print(f"🔍 MCP Query {i+1}/{min(len(search_terms), max_queries)}: '{term[:50]}{'...' if len(term) > 50 else ''}'")
                
                # Query MCP for this search term with tracing
                start_time = time.time()
                response = self.mcp_client.search(term)
                elapsed_ms = (time.time() - start_time) * 1000
                
                # Trace the MCP call
                if LANGFUSE_AVAILABLE and langfuse_manager.enabled:
                    langfuse_manager.trace_mcp_call(
                        server_name=getattr(self.mcp_client, 'default_server', 'unknown'),
                        query=term,
                        response=response[:500] if response else "No response",
                        latency_ms=elapsed_ms,
                        metadata={
                            "query_index": i + 1,
                            "total_queries": min(len(search_terms), max_queries),
                            "response_length": len(response) if response else 0,
                            "success": response and "Error:" not in response
                        }
                    )
                
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
        
        # Use proper with statement for context management
        if LANGFUSE_AVAILABLE and langfuse_manager.enabled:
            with langfuse_manager.trace_span(
                "dspy_mcp_research_pipeline",
                metadata={
                    "query": user_query[:100],
                    "query_length": len(user_query)
                },
                tags=["research", "dspy", "mcp"]
            ) as span:
                try:
                    pipeline_start = time.time()
                    print(f"🚀 Starting DSPy+MCP research pipeline for: '{user_query[:60]}...'")
                    
                    # Step 1: Analyze query with DSPy
                    analysis = await self.analyze_query_structure(user_query)
                    
                    # Step 2: Gather information via MCP based on DSPy analysis  
                    external_info = await self.gather_information(analysis['search_terms'])
                    
                    # Step 3: Process everything through DSPy structured pipeline
                    print("🧠 Processing through DSPy structured reasoning pipeline...")
                    synthesis_start = time.time()
                    result = self.research_pipeline(
                        user_query=user_query,
                        external_info=external_info
                    )
                    synthesis_time = (time.time() - synthesis_start) * 1000
                    
                    total_time = (time.time() - pipeline_start) * 1000
                    
                    # Update span with complete result
                    if span:
                        span.update(
                            metadata={
                                "total_latency_ms": total_time,
                                "synthesis_latency_ms": synthesis_time,
                                "query_type": analysis['query_type'],
                                "confidence": result.confidence_level,
                                "search_terms_used": len(analysis['search_terms'])
                            },
                            tags=["complete", result.query_type]
                        )
                    
                    print("✅ DSPy+MCP pipeline completed successfully")
                    return result
                    
                except Exception as e:
                    print(f"❌ Error in DSPy pipeline: {e}")
                    
                    # Create a fallback result
                    return ResearchPiplineResult(
                        main_topic=analysis.get('main_topic', 'Unknown') if 'analysis' in locals() else user_query[:50],
                        sub_topics=analysis.get('sub_topics', [user_query]) if 'analysis' in locals() else [user_query],
                        query_type=analysis.get('query_type', 'general') if 'analysis' in locals() else 'general',
                        information_needs=analysis.get('information_needs', 'General information') if 'analysis' in locals() else 'General information',
                        search_terms=analysis.get('search_terms', [user_query]) if 'analysis' in locals() else [user_query],
                        key_insights="Analysis completed with limited DSPy processing due to error.",
                        relevance_assessment="Unable to fully assess relevance.",
                        gaps_identified="Processing error prevented full gap analysis.",
                        synthesized_context=f"Query: {user_query}\nExternal Info: {external_info[:500] if 'external_info' in locals() else 'N/A'}...",
                        direct_answer="I encountered an error during structured processing, but gathered some information.",
                        supporting_details=external_info[:1000] + "..." if 'external_info' in locals() and len(external_info) > 1000 else external_info if 'external_info' in locals() else "No information gathered",
                        actionable_insights="Review the gathered information and try reformulating the query.",
                        confidence_level="low - processing error occurred",
                        external_info=external_info if 'external_info' in locals() else ""
                    )
        else:
            # No tracing - just run the pipeline
            try:
                pipeline_start = time.time()
                print(f"🚀 Starting DSPy+MCP research pipeline for: '{user_query[:60]}...'")
                
                # Step 1: Analyze query with DSPy
                analysis = await self.analyze_query_structure(user_query)
                
                # Step 2: Gather information via MCP based on DSPy analysis  
                external_info = await self.gather_information(analysis['search_terms'])
                
                # Step 3: Process everything through DSPy structured pipeline
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