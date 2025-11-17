"""
Enhanced Research Agent package.

This package provides a research agent that combines:
- OpenManus ReAct agent framework for execution coordination
- DSPy structured reasoning for query analysis and response generation
- MCP (Model Control Protocol) for external information gathering

The integration creates a sophisticated research pipeline with structured thinking.
"""

from .app import EnhancedResearchAgent, run_enhanced_agent, create_agent
from .mcp_client import MCPClient
from .dspy_mcp_integration import DSPyMCPIntegration
from .dspy_modules import (
    StructuredResearchPipeline,
    QuickAnalysis,
    ResearchPiplineResult,
    QueryAnalysis,
    InformationSynthesis,
    ResponseGeneration
)

__version__ = "0.1.0"
__all__ = [
    # Main application
    "EnhancedResearchAgent",
    "create_agent",
    "run_enhanced_agent",

    # Integration layer
    "DSPyMCPIntegration",
    "MCPClient",

    # DSPy modules and signatures
    "StructuredResearchPipeline",
    "QuickAnalysis",
    "ResearchPiplineResult",
    "QueryAnalysis",
    "InformationSynthesis",
    "ResponseGeneration"
] 