"""
UI Integration Example for Unified MCP Client

This module demonstrates how to integrate the unified MCP client with UI controls
(Streamlit, FastAPI, etc.) using the exposed routing hints API.

The key principle: UI controls (dropdowns, buttons, mode selectors) map directly
to the unified backend API, preventing drift between UI and core behavior.
"""

import asyncio
from typing import Dict, Any, List, Optional
import streamlit as st

from .unified_integration import UnifiedDSPyMCPIntegration
from .mcp_config import RoutingStrategy


class UIIntegrationHelper:
    """
    Helper class for integrating unified MCP client with UI frameworks.

    Provides methods to:
    - Get routing hints for UI controls
    - Convert UI selections to API calls
    - Format results for display
    """

    def __init__(self, integration: UnifiedDSPyMCPIntegration):
        """
        Initialize UI integration helper.

        Args:
            integration: UnifiedDSPyMCPIntegration instance
        """
        self.integration = integration
        self._routing_hints = None

    def get_routing_hints(self) -> Dict[str, Any]:
        """Get routing hints (cached for performance)"""
        if self._routing_hints is None:
            self._routing_hints = self.integration.get_routing_hints()
        return self._routing_hints

    def get_server_choices(self) -> List[Dict[str, str]]:
        """
        Get server choices formatted for UI display.

        Returns:
            List of dicts with 'name', 'description', 'type', 'capabilities'
        """
        hints = self.get_routing_hints()
        return [
            {
                "name": server["name"],
                "description": server["description"],
                "type": server["type"],
                "capabilities": ", ".join(server["capabilities"]),
                "enabled": server["enabled"]
            }
            for server in hints["available_servers"]
            if server["enabled"]
        ]

    def get_strategy_choices(self) -> List[Dict[str, str]]:
        """
        Get routing strategy choices formatted for UI display.

        Returns:
            List of dicts with 'value' and 'description'
        """
        return [
            {
                "value": "auto",
                "label": "Auto",
                "description": "Automatically select best server(s) based on query"
            },
            {
                "value": "manual",
                "label": "Manual",
                "description": "Manually select specific server(s)"
            },
            {
                "value": "multi",
                "label": "Multi",
                "description": "Query multiple relevant servers and combine results"
            }
        ]

    def get_capability_groups(self) -> Dict[str, List[str]]:
        """
        Group servers by capability for organized UI display.

        Returns:
            Dict mapping capability names to lists of server names
        """
        hints = self.get_routing_hints()
        capability_groups = {}

        for server in hints["available_servers"]:
            if not server["enabled"]:
                continue

            for capability in server["capabilities"]:
                if capability not in capability_groups:
                    capability_groups[capability] = []
                capability_groups[capability].append(server["name"])

        return capability_groups

    def format_routing_rules_for_display(self) -> str:
        """
        Format routing rules as human-readable text for UI display.

        Returns:
            Formatted string describing routing rules
        """
        hints = self.get_routing_hints()
        rules = hints["routing_rules"]

        if not rules:
            return "No routing rules configured."

        lines = ["**Query Routing Rules:**"]
        for topic, servers in rules.items():
            # Convert topic from snake_case to Title Case
            topic_display = topic.replace('_', ' ').title()
            servers_display = ", ".join(servers)
            lines.append(f"- **{topic_display}**: {servers_display}")

        return "\n".join(lines)


# ==================== Streamlit Integration Example ====================

def create_streamlit_ui(integration: UnifiedDSPyMCPIntegration):
    """
    Example Streamlit UI that uses the unified backend.

    This demonstrates how to create UI controls that map directly to the
    backend API, ensuring no drift between UI and core behavior.
    """
    helper = UIIntegrationHelper(integration)

    st.title("🧠 Enhanced Research Agent")
    st.markdown("Powered by Unified MCP Client with DSPy Integration")

    # Sidebar: Configuration and routing controls
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Strategy selector
        st.subheader("Routing Strategy")
        strategies = helper.get_strategy_choices()
        strategy_labels = [s["label"] for s in strategies]
        strategy_descriptions = {s["label"]: s["description"] for s in strategies}

        selected_strategy_label = st.radio(
            "Select mode:",
            strategy_labels,
            help="Choose how servers are selected for your query"
        )

        # Show description for selected strategy
        st.info(strategy_descriptions[selected_strategy_label])

        # Convert label back to RoutingStrategy enum
        strategy_map = {"Auto": RoutingStrategy.AUTO, "Manual": RoutingStrategy.MANUAL, "Multi": RoutingStrategy.MULTI}
        selected_strategy = strategy_map[selected_strategy_label]

        # Server selector (only shown in manual mode)
        selected_servers = None
        if selected_strategy == RoutingStrategy.MANUAL:
            st.subheader("Select Servers")
            server_choices = helper.get_server_choices()
            server_names = [s["name"] for s in server_choices]
            server_descriptions = {s["name"]: f"{s['description']} ({s['type']})" for s in server_choices}

            selected_servers = st.multiselect(
                "Choose one or more servers:",
                server_names,
                help="Select which servers to query",
                format_func=lambda x: f"{x}: {server_descriptions[x]}"
            )

        # Show routing rules
        st.subheader("📋 Routing Rules")
        with st.expander("View routing rules"):
            st.markdown(helper.format_routing_rules_for_display())

        # Show available servers by capability
        st.subheader("🔧 Available Servers")
        with st.expander("View servers by capability"):
            capability_groups = helper.get_capability_groups()
            for capability, servers in capability_groups.items():
                st.markdown(f"**{capability.replace('_', ' ').title()}**")
                st.markdown(f"- {', '.join(servers)}")

    # Main area: Query input and results
    st.header("🔍 Search")

    query = st.text_area(
        "Enter your research query:",
        height=100,
        placeholder="What would you like to know?"
    )

    use_dspy = st.checkbox(
        "Use DSPy structured reasoning",
        value=True,
        help="Enable DSPy for advanced query analysis and result synthesis"
    )

    if st.button("🚀 Search", type="primary", disabled=not query):
        with st.spinner("Researching..."):
            # Execute search using unified backend
            result = asyncio.run(
                integration.research(
                    query=query,
                    servers=selected_servers if selected_servers else None,
                    strategy=selected_strategy,
                    use_dspy=use_dspy
                )
            )

            # Display results
            st.success("✅ Research complete!")

            # Show metadata
            with st.expander("📊 Execution Metadata"):
                metadata = result["metadata"]
                col1, col2, col3 = st.columns(3)
                col1.metric("Strategy", metadata["strategy"])
                col2.metric("Servers Used", len(metadata["servers_used"]))
                col3.metric("Execution Time", f"{metadata['execution_time']:.2f}s")
                st.write("**Servers:**", ", ".join(metadata["servers_used"]))

            # Show DSPy analysis (if available)
            if result.get("analysis"):
                st.subheader("🧠 Query Analysis")
                analysis = result["analysis"]
                st.write(f"**Primary Topic:** {analysis['primary_topic']}")
                st.write(f"**Query Type:** {analysis['query_type']}")
                st.write(f"**Suggested Sources:** {', '.join(analysis['suggested_sources'])}")
                with st.expander("View reasoning"):
                    st.write(analysis["reasoning"])

            # Show MCP results
            st.subheader("📚 Information Gathered")
            mcp_results = result["mcp_results"]
            if isinstance(mcp_results, dict):
                # Multiple servers
                for server_name, content in mcp_results.items():
                    with st.expander(f"From {server_name}"):
                        if content.startswith("Error:"):
                            st.error(content)
                        else:
                            st.write(content)
            else:
                # Single server
                st.write(mcp_results)

            # Show synthesis (if available)
            if result.get("synthesis"):
                st.subheader("🎯 Synthesized Answer")
                synthesis = result["synthesis"]
                st.write(synthesis["answer"])

                col1, col2 = st.columns(2)
                col1.metric("Confidence", f"{synthesis['confidence']:.0%}")
                col2.write(f"**Sources:** {', '.join(synthesis['sources_used'])}")

                with st.expander("View reasoning"):
                    st.write(synthesis["reasoning"])


# ==================== FastAPI Integration Example ====================

def create_fastapi_endpoints(app, integration: UnifiedDSPyMCPIntegration):
    """
    Example FastAPI endpoints that use the unified backend.

    This demonstrates how to create REST API endpoints that expose
    the same routing controls as the UI.
    """
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    from typing import Optional, List

    helper = UIIntegrationHelper(integration)

    # Request models
    class SearchRequest(BaseModel):
        query: str
        servers: Optional[List[str]] = None
        strategy: Optional[str] = None
        use_dspy: bool = True

    class RoutingHintsResponse(BaseModel):
        available_servers: List[Dict[str, Any]]
        routing_rules: Dict[str, List[str]]
        strategies: List[str]
        default_strategy: str
        fallback_servers: List[str]

    # Endpoints
    @app.get("/api/routing-hints", response_model=RoutingHintsResponse)
    async def get_routing_hints():
        """Get routing configuration hints for UI/API clients"""
        return helper.get_routing_hints()

    @app.get("/api/servers")
    async def get_servers():
        """Get list of available servers with metadata"""
        return helper.get_server_choices()

    @app.get("/api/servers/by-capability/{capability}")
    async def get_servers_by_capability(capability: str):
        """Get servers that have a specific capability"""
        servers = integration.get_servers_by_capability(capability)
        return {"capability": capability, "servers": servers}

    @app.post("/api/search")
    async def search(request: SearchRequest):
        """
        Execute a research query with specified routing strategy.

        The routing parameters (servers, strategy) map directly to the
        backend API, ensuring consistency with UI controls.
        """
        # Validate strategy
        strategy_enum = None
        if request.strategy:
            try:
                strategy_enum = RoutingStrategy(request.strategy)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid strategy. Valid options: {[s.value for s in RoutingStrategy]}"
                )

        # Execute search
        try:
            result = await integration.research(
                query=request.query,
                servers=request.servers,
                strategy=strategy_enum,
                use_dspy=request.use_dspy
            )
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/quick-search")
    async def quick_search(query: str, servers: Optional[List[str]] = None):
        """Quick search without DSPy overhead"""
        try:
            result = await integration.quick_search(query=query, servers=servers)
            return {"query": query, "result": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# ==================== Usage Example ====================

if __name__ == "__main__":
    """
    Example usage demonstrating the unified integration.
    """
    import sys

    # Create integration
    integration = UnifiedDSPyMCPIntegration(
        llm_model="gpt-3.5-turbo",
        dspy_cache=True
    )

    # Example 1: Get routing hints for UI
    helper = UIIntegrationHelper(integration)
    hints = helper.get_routing_hints()
    print("Available routing strategies:", hints["strategies"])
    print("Default strategy:", hints["default_strategy"])

    # Example 2: Execute search with auto routing
    async def test_auto_search():
        result = await integration.research(
            query="What are the latest developments in quantum computing?",
            strategy=RoutingStrategy.AUTO,
            use_dspy=True
        )
        print("\n=== Auto Search Result ===")
        print(f"Servers used: {result['metadata']['servers_used']}")
        print(f"Execution time: {result['metadata']['execution_time']:.2f}s")

    # Example 3: Execute search with manual server selection
    async def test_manual_search():
        result = await integration.research(
            query="AAPL stock price",
            servers=["finance"],
            strategy=RoutingStrategy.MANUAL,
            use_dspy=False
        )
        print("\n=== Manual Search Result ===")
        print(f"Result: {result['mcp_results']}")

    # Example 4: Execute multi-server search
    async def test_multi_search():
        result = await integration.research(
            query="AI research papers and GitHub projects",
            strategy=RoutingStrategy.MULTI,
            use_dspy=True
        )
        print("\n=== Multi Search Result ===")
        print(f"Servers queried: {result['metadata']['servers_used']}")
        for server, content in result['mcp_results'].items():
            print(f"\nFrom {server}:")
            print(content[:200] + "..." if len(content) > 200 else content)

    # Run examples
    asyncio.run(test_auto_search())
    asyncio.run(test_manual_search())
    asyncio.run(test_multi_search())
