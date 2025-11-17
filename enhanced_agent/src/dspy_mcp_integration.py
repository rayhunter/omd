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
from pathlib import Path

# Load environment variables from .env file (if available)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not available, using environment variables only")
    # Define a dummy load_dotenv function to prevent errors
    def load_dotenv():
        pass

from .dspy_modules import StructuredResearchPipeline, QuickAnalysis, ResearchPiplineResult
from .mcp_client import MCPClient

# Import Langfuse integration (optional, from project root)
try:
    import sys
    # Only temporarily add to path if langfuse_integration is needed
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from langfuse_integration import langfuse_manager
    sys.path.remove(str(project_root))  # Clean up after import
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
                 dspy_cache: bool = True,
                 enable_step_cache: bool = True):
        """
        Initialize the DSPy-MCP integration.

        Args:
            mcp_config_path: Path to MCP configuration file
            llm_model: LLM model to use for DSPy reasoning
            dspy_cache: Whether to enable DSPy caching
            enable_step_cache: Whether to cache intermediate steps for failure recovery
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
            'max_concurrent_queries': 3,  # Maximum concurrent MCP queries
            'enable_step_cache': enable_step_cache,  # Enable step-level caching
        }

        # Semaphore for controlling concurrent MCP queries
        self._mcp_semaphore = asyncio.Semaphore(self.config['max_concurrent_queries'])

        # Step-level cache for failure recovery (query -> {analysis, external_info})
        self._step_cache = {} if enable_step_cache else None
        
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
            elif "gemma" in model_name.lower() or "llama" in model_name.lower() or "qwen" in model_name.lower():
                # For Ollama models, use the ollama/ prefix
                model_path = f"ollama/{model_name}"
            elif "phi" in model_name.lower() or "tinyllama" in model_name.lower():
                # For Hugging Face models, use the huggingface/ prefix
                model_path = f"huggingface/{model_name}"
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

        Uses asyncio.gather for concurrent queries with semaphore-based rate limiting.

        Args:
            search_terms: List of search terms from DSPy analysis
            max_queries: Maximum number of queries to make (defaults to config)

        Returns:
            Aggregated information from all MCP queries
        """
        max_queries = max_queries or self.config['max_mcp_queries']

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

        # Limit search terms to max_queries
        limited_terms = search_terms[:max_queries]

        async def _query_with_semaphore(term: str, index: int) -> Dict[str, Any]:
            """Execute a single MCP query with semaphore-based rate limiting."""
            async with self._mcp_semaphore:
                try:
                    print(f"🔍 MCP Query {index+1}/{len(limited_terms)}: '{term[:50]}{'...' if len(term) > 50 else ''}'")

                    # Query MCP for this search term with tracing
                    start_time = time.time()
                    response = await self.mcp_client.search(term)
                    elapsed_ms = (time.time() - start_time) * 1000

                    # Trace the MCP call
                    if LANGFUSE_AVAILABLE and langfuse_manager.enabled:
                        langfuse_manager.trace_mcp_call(
                            server_name=getattr(self.mcp_client, 'default_server', 'unknown'),
                            query=term,
                            response=response[:500] if response else "No response",
                            latency_ms=elapsed_ms,
                            metadata={
                                "query_index": index + 1,
                                "total_queries": len(limited_terms),
                                "response_length": len(response) if response else 0,
                                "success": response and "Error:" not in response
                            }
                        )

                    if response and "Error:" not in response:
                        print(f"   ✅ Got {len(response)} characters of information")
                        return {
                            "term": term,
                            "response": response,
                            "success": True,
                            "error": None
                        }
                    else:
                        print(f"   ⚠️  Query failed or returned error: {response[:100]}...")
                        return {
                            "term": term,
                            "response": response,
                            "success": False,
                            "error": "Query returned error"
                        }

                except Exception as e:
                    print(f"   ❌ MCP query failed: {e}")
                    return {
                        "term": term,
                        "response": None,
                        "success": False,
                        "error": str(e)
                    }

        # Execute all queries concurrently with semaphore-based rate limiting
        print(f"🚀 Starting {len(limited_terms)} concurrent MCP queries (max {self.config['max_concurrent_queries']} at once)...")
        query_tasks = [
            _query_with_semaphore(term, i)
            for i, term in enumerate(limited_terms)
        ]
        results = await asyncio.gather(*query_tasks, return_exceptions=True)

        # Process results
        gathered_info = []
        for result in results:
            if isinstance(result, Exception):
                gathered_info.append(f"Query Error: {str(result)}\n---")
            elif result["success"]:
                gathered_info.append(f"Query: {result['term']}\nResponse: {result['response']}\n---")
            else:
                error_msg = result['error'] or result.get('response', 'Unknown error')
                gathered_info.append(f"Query: {result['term']}\nError: {error_msg}\n---")

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

        # Initialize step results before try block for safe fallback access
        analysis = None
        external_info = None

        # Check for cached intermediate results
        cache_key = user_query[:100]  # Use truncated query as cache key
        if self._step_cache is not None and cache_key in self._step_cache:
            cached = self._step_cache[cache_key]
            analysis = cached.get('analysis')
            external_info = cached.get('external_info')
            print(f"♻️  Found cached intermediate results for query")

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

                    # Step 1: Analyze query with DSPy (skip if cached)
                    if analysis is None:
                        analysis = await self.analyze_query_structure(user_query)
                        # Cache analysis step
                        if self._step_cache is not None:
                            self._step_cache[cache_key] = {'analysis': analysis}

                    # Step 2: Gather information via MCP based on DSPy analysis (skip if cached)
                    if external_info is None:
                        external_info = await self.gather_information(analysis['search_terms'])
                        # Cache external_info step
                        if self._step_cache is not None:
                            self._step_cache[cache_key]['external_info'] = external_info

                    # Step 3: Process everything through DSPy structured pipeline
                    print("🧠 Processing through DSPy structured reasoning pipeline...")
                    synthesis_start = time.time()
                    result = self.research_pipeline(
                        user_query=user_query,
                        external_info=external_info
                    )
                    synthesis_time = (time.time() - synthesis_start) * 1000

                    total_time = (time.time() - pipeline_start) * 1000

                    # Clear cache after successful completion
                    if self._step_cache is not None and cache_key in self._step_cache:
                        del self._step_cache[cache_key]

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

                    # Prepare safe fallback defaults
                    fallback_defaults = {
                        'main_topic': user_query[:50] + "..." if len(user_query) > 50 else user_query,
                        'sub_topics': [user_query],
                        'query_type': 'general',
                        'information_needs': 'General information about the topic',
                        'search_terms': [user_query]
                    }

                    # Create a fallback result using cached or default values
                    return ResearchPiplineResult(
                        main_topic=(analysis or fallback_defaults).get('main_topic', fallback_defaults['main_topic']),
                        sub_topics=(analysis or fallback_defaults).get('sub_topics', fallback_defaults['sub_topics']),
                        query_type=(analysis or fallback_defaults).get('query_type', fallback_defaults['query_type']),
                        information_needs=(analysis or fallback_defaults).get('information_needs', fallback_defaults['information_needs']),
                        search_terms=(analysis or fallback_defaults).get('search_terms', fallback_defaults['search_terms']),
                        key_insights="Analysis completed with limited DSPy processing due to error.",
                        relevance_assessment="Unable to fully assess relevance.",
                        gaps_identified="Processing error prevented full gap analysis.",
                        synthesized_context=f"Query: {user_query}\nExternal Info: {external_info[:500] if external_info else 'N/A'}...",
                        direct_answer="I encountered an error during structured processing, but gathered some information.",
                        supporting_details=external_info[:1000] + "..." if external_info and len(external_info) > 1000 else external_info or "No information gathered",
                        actionable_insights="Review the gathered information and try reformulating the query.",
                        confidence_level="low - processing error occurred",
                        external_info=external_info or ""
                    )
        else:
            # No tracing - just run the pipeline
            try:
                pipeline_start = time.time()
                print(f"🚀 Starting DSPy+MCP research pipeline for: '{user_query[:60]}...'")

                # Step 1: Analyze query with DSPy (skip if cached)
                if analysis is None:
                    analysis = await self.analyze_query_structure(user_query)
                    # Cache analysis step
                    if self._step_cache is not None:
                        self._step_cache[cache_key] = {'analysis': analysis}

                # Step 2: Gather information via MCP based on DSPy analysis (skip if cached)
                if external_info is None:
                    external_info = await self.gather_information(analysis['search_terms'])
                    # Cache external_info step
                    if self._step_cache is not None:
                        self._step_cache[cache_key]['external_info'] = external_info

                # Step 3: Process everything through DSPy structured pipeline
                print("🧠 Processing through DSPy structured reasoning pipeline...")
                result = self.research_pipeline(
                    user_query=user_query,
                    external_info=external_info
                )

                # Clear cache after successful completion
                if self._step_cache is not None and cache_key in self._step_cache:
                    del self._step_cache[cache_key]

                print("✅ DSPy+MCP pipeline completed successfully")
                return result

            except Exception as e:
                print(f"❌ Error in DSPy pipeline: {e}")

                # Prepare safe fallback defaults
                fallback_defaults = {
                    'main_topic': user_query[:50] + "..." if len(user_query) > 50 else user_query,
                    'sub_topics': [user_query],
                    'query_type': 'general',
                    'information_needs': 'General information about the topic',
                    'search_terms': [user_query]
                }

                # Create a fallback result using cached or default values
                return ResearchPiplineResult(
                    main_topic=(analysis or fallback_defaults).get('main_topic', fallback_defaults['main_topic']),
                    sub_topics=(analysis or fallback_defaults).get('sub_topics', fallback_defaults['sub_topics']),
                    query_type=(analysis or fallback_defaults).get('query_type', fallback_defaults['query_type']),
                    information_needs=(analysis or fallback_defaults).get('information_needs', fallback_defaults['information_needs']),
                    search_terms=(analysis or fallback_defaults).get('search_terms', fallback_defaults['search_terms']),
                    key_insights="Analysis completed with limited DSPy processing due to error.",
                    relevance_assessment="Unable to fully assess relevance.",
                    gaps_identified="Processing error prevented full gap analysis.",
                    synthesized_context=f"Query: {user_query}\nExternal Info: {external_info[:500] if external_info else 'N/A'}...",
                    direct_answer="I encountered an error during structured processing, but gathered some information.",
                    supporting_details=external_info[:1000] + "..." if external_info and len(external_info) > 1000 else external_info or "No information gathered",
                    actionable_insights="Review the gathered information and try reformulating the query.",
                    confidence_level="low - processing error occurred",
                    external_info=external_info or ""
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