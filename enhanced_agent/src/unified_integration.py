"""
Unified DSPy-MCP Integration with Routing Hints

This module provides an updated integration layer that uses the unified MCP client
and exposes routing hints for UI/API control mapping.
"""

import asyncio
import dspy
from typing import Dict, Any, List, Optional
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .unified_mcp_client import UnifiedMCPClient
from .mcp_config import RoutingStrategy, load_mcp_config
from .dspy_modules import StructuredResearchPipeline, QuickAnalysis, ResearchPiplineResult

# Import Langfuse integration (optional)
try:
    project_root = Path(__file__).parent.parent.parent
    import sys
    sys.path.insert(0, str(project_root))
    from langfuse_integration import langfuse_manager
    sys.path.remove(str(project_root))
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    langfuse_manager = None


class UnifiedDSPyMCPIntegration:
    """
    Unified integration combining DSPy structured reasoning with the unified MCP client.

    Features:
    - Uses unified MCP client with full async support
    - Exposes routing hints for UI control mapping
    - Supports auto/manual/multi routing modes
    - Maintains backward compatibility with existing DSPy integration
    """

    def __init__(
        self,
        mcp_config_path: Optional[str] = None,
        llm_model: str = "gpt-3.5-turbo",
        dspy_cache: bool = True,
        enable_step_cache: bool = True,
        default_strategy: Optional[RoutingStrategy] = None
    ):
        """
        Initialize the unified DSPy-MCP integration.

        Args:
            mcp_config_path: Path to MCP configuration file (searches defaults if None)
            llm_model: LLM model to use for DSPy reasoning
            dspy_cache: Whether to enable DSPy caching
            enable_step_cache: Whether to cache intermediate steps
            default_strategy: Default routing strategy (None uses config default)
        """
        # Initialize unified MCP client
        self.mcp_client = UnifiedMCPClient(mcp_config_path)

        # Store default strategy
        if default_strategy:
            self.mcp_client.config.server_selection_strategy = default_strategy

        # Initialize DSPy
        self._setup_dspy(llm_model, dspy_cache)

        # Initialize DSPy modules
        self.research_pipeline = StructuredResearchPipeline()
        self.quick_analysis = QuickAnalysis()

        # Step caching
        self.enable_step_cache = enable_step_cache
        self._step_cache = {}

        # Langfuse tracking
        self.langfuse_session_id = None
        if LANGFUSE_AVAILABLE and langfuse_manager:
            self.langfuse_session_id = langfuse_manager.create_session(
                name="UnifiedDSPyMCPSession",
                metadata={"llm_model": llm_model}
            )

    def _setup_dspy(self, llm_model: str, use_cache: bool):
        """Setup DSPy with the specified LLM"""
        try:
            # Configure DSPy LLM
            lm = dspy.OpenAI(model=llm_model, max_tokens=2000)
            dspy.settings.configure(lm=lm, cache=use_cache)
            print(f"✅ DSPy configured with model: {llm_model}")
        except Exception as e:
            print(f"⚠️  Failed to configure DSPy: {e}")
            raise

    # ==================== Routing Control API ====================

    def get_routing_hints(self) -> Dict[str, Any]:
        """
        Get routing configuration hints for UI/API integration.

        Returns:
            Dict containing:
            - available_servers: List of enabled servers with metadata
            - routing_rules: Topic-based routing rules
            - strategies: Available routing strategies
            - default_strategy: Current default strategy
            - fallback_servers: List of fallback servers
        """
        return self.mcp_client.get_routing_hints()

    def set_routing_strategy(self, strategy: RoutingStrategy):
        """
        Set the default routing strategy.

        Args:
            strategy: The routing strategy to use (auto/manual/multi)
        """
        self.mcp_client.config.server_selection_strategy = strategy

    def get_available_servers(self) -> List[str]:
        """Get list of available (enabled) server names"""
        return self.mcp_client.list_enabled_servers()

    def get_servers_by_capability(self, capability: str) -> List[str]:
        """Get servers that have a specific capability"""
        return self.mcp_client.get_servers_by_capability(capability)

    # ==================== Research Methods ====================

    async def research(
        self,
        query: str,
        servers: Optional[List[str]] = None,
        strategy: Optional[RoutingStrategy] = None,
        use_dspy: bool = True
    ) -> Dict[str, Any]:
        """
        Perform research using DSPy analysis + MCP information gathering.

        Args:
            query: The research query
            servers: Optional list of servers to use (for manual mode)
            strategy: Optional routing strategy override
            use_dspy: Whether to use DSPy structured reasoning

        Returns:
            Dict containing:
            - query: Original query
            - analysis: DSPy query analysis (if use_dspy=True)
            - mcp_results: Results from MCP servers
            - synthesis: Synthesized result (if use_dspy=True)
            - metadata: Execution metadata
        """
        start_time = asyncio.get_event_loop().time()

        # Track with Langfuse
        if LANGFUSE_AVAILABLE and self.langfuse_session_id:
            trace_id = langfuse_manager.start_trace(
                session_id=self.langfuse_session_id,
                name="unified_research",
                metadata={"query": query, "servers": servers, "strategy": strategy}
            )

        result = {
            "query": query,
            "analysis": None,
            "mcp_results": None,
            "synthesis": None,
            "metadata": {
                "servers_used": [],
                "strategy": strategy.value if strategy else self.mcp_client.config.server_selection_strategy.value,
                "used_dspy": use_dspy,
                "execution_time": 0
            }
        }

        try:
            # Step 1: DSPy query analysis (if enabled)
            if use_dspy:
                analysis = self.quick_analysis(query=query)
                result["analysis"] = {
                    "primary_topic": analysis.primary_topic,
                    "query_type": analysis.query_type,
                    "suggested_sources": analysis.suggested_sources,
                    "reasoning": analysis.reasoning
                }

                # Use DSPy suggestions to inform server selection if no manual override
                if not servers and not strategy:
                    # Try to map suggested sources to servers
                    servers = self._map_sources_to_servers(analysis.suggested_sources)

            # Step 2: MCP information gathering
            mcp_results = await self.mcp_client.search(
                query=query,
                servers=servers,
                strategy=strategy
            )
            result["mcp_results"] = mcp_results

            # Track which servers were actually used
            if isinstance(mcp_results, dict):
                result["metadata"]["servers_used"] = list(mcp_results.keys())
            else:
                # Single server result - determine which one was used
                if servers:
                    result["metadata"]["servers_used"] = [servers[0]]
                else:
                    result["metadata"]["servers_used"] = [self.mcp_client.config.default_server]

            # Step 3: DSPy synthesis (if enabled)
            if use_dspy and mcp_results:
                # Combine MCP results into a single context string
                if isinstance(mcp_results, dict):
                    context = "\n\n".join([
                        f"From {server}:\n{content}"
                        for server, content in mcp_results.items()
                        if not content.startswith("Error:")
                    ])
                else:
                    context = mcp_results

                if context:
                    # Use research pipeline for synthesis
                    pipeline_result = self.research_pipeline(
                        query=query,
                        context=context
                    )
                    result["synthesis"] = {
                        "answer": pipeline_result.answer,
                        "reasoning": pipeline_result.reasoning,
                        "confidence": pipeline_result.confidence,
                        "sources_used": pipeline_result.sources_used
                    }

        except Exception as e:
            result["error"] = str(e)

        # Calculate execution time
        end_time = asyncio.get_event_loop().time()
        result["metadata"]["execution_time"] = end_time - start_time

        # End Langfuse trace
        if LANGFUSE_AVAILABLE and self.langfuse_session_id:
            langfuse_manager.end_trace(
                trace_id=trace_id,
                output=result,
                metadata=result["metadata"]
            )

        return result

    def _map_sources_to_servers(self, suggested_sources: List[str]) -> Optional[List[str]]:
        """
        Map DSPy suggested sources to actual MCP server names.

        Args:
            suggested_sources: List of source suggestions from DSPy

        Returns:
            List of server names, or None if no mapping found
        """
        # Mapping of common source types to server capabilities
        source_to_capability = {
            "academic": "scientific_research",
            "scientific": "scientific_research",
            "research": "scientific_research",
            "news": "current_events",
            "web": "web_search",
            "wikipedia": "encyclopedic_knowledge",
            "encyclopedia": "encyclopedic_knowledge",
            "github": "code_search",
            "code": "code_search"
        }

        servers = []
        for source in suggested_sources:
            source_lower = source.lower()
            for keyword, capability in source_to_capability.items():
                if keyword in source_lower:
                    # Find servers with this capability
                    matching_servers = self.mcp_client.get_servers_by_capability(capability)
                    servers.extend(matching_servers)
                    break

        # Remove duplicates while preserving order
        if servers:
            return list(dict.fromkeys(servers))
        return None

    async def quick_search(
        self,
        query: str,
        servers: Optional[List[str]] = None
    ) -> str:
        """
        Quick search without DSPy overhead (useful for simple queries).

        Args:
            query: The search query
            servers: Optional list of servers to use

        Returns:
            Search result as string
        """
        result = await self.mcp_client.search(
            query=query,
            servers=servers,
            strategy=RoutingStrategy.AUTO
        )

        # Convert dict results to string if needed
        if isinstance(result, dict):
            return "\n\n".join([
                f"From {server}:\n{content}"
                for server, content in result.items()
            ])
        return result

    # ==================== Utility Methods ====================

    async def close(self):
        """Close the integration and cleanup resources"""
        await self.mcp_client.close()

        if LANGFUSE_AVAILABLE and self.langfuse_session_id:
            langfuse_manager.end_session(self.langfuse_session_id)

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


# Convenience function for backward compatibility
def create_integration(
    mcp_config_path: Optional[str] = None,
    llm_model: str = "gpt-3.5-turbo",
    **kwargs
) -> UnifiedDSPyMCPIntegration:
    """
    Create a unified DSPy-MCP integration instance.

    Args:
        mcp_config_path: Path to MCP config file
        llm_model: LLM model for DSPy
        **kwargs: Additional arguments passed to UnifiedDSPyMCPIntegration

    Returns:
        UnifiedDSPyMCPIntegration instance
    """
    return UnifiedDSPyMCPIntegration(
        mcp_config_path=mcp_config_path,
        llm_model=llm_model,
        **kwargs
    )
