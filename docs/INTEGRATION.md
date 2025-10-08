# 🔗 Integration Guide

Complete guide to integrating the Enhanced Research Agent with OpenManus and extending functionality.

## 📋 Table of Contents

- [Overview](#overview)
- [OpenManus Integration](#openmanus-integration)
- [Tool Integration](#tool-integration)
- [Custom MCP Servers](#custom-mcp-servers)
- [API Integration](#api-integration)
- [Extension Points](#extension-points)

## 🌟 Overview

The Enhanced Research Agent is designed to integrate seamlessly with the OpenManus framework as a specialized tool, while also being usable as a standalone application. This guide covers:

- Using the agent as an OpenManus tool
- Creating custom MCP servers
- Integrating with external systems
- Extending functionality

## 🤖 OpenManus Integration

### How It Works

The enhanced agent integrates with OpenManus through a tool interface:

```
┌─────────────────────┐
│  OpenManus Agent    │
│  (Main Orchestrator)│
└──────────┬──────────┘
           │
           │ Delegates complex tasks
           ▼
┌─────────────────────┐
│  Enhanced Agent Tool│
│  (Research Specialist)
└──────────┬──────────┘
           │
           │ Uses
           ▼
┌─────────────────────┐
│  DSPy + MCP Pipeline│
│  (Structured Research)
└─────────────────────┘
```

### Architecture

1. **OpenManus Agent** - General-purpose agent with tools for coding, file operations, and web browsing
2. **Enhanced Agent Tool** - Bridge that exposes the enhanced agent as a tool
3. **Enhanced Agent** - Specialized in research, complex reasoning, and information synthesis

### Benefits

- **Complementary Strengths** - Combines general-purpose capabilities with specialized research
- **Seamless Delegation** - Main agent can delegate complex queries automatically
- **Resource Efficiency** - Each agent optimized for its domain
- **Modular Design** - Easy to enable/disable or replace components

## 🛠️ Tool Integration

### Enhanced Agent as OpenManus Tool

The `EnhancedAgentTool` class in `OpenManus/app/tool/enhanced_agent_tool.py` provides the integration:

```python
from OpenManus.app.tool.enhanced_agent_tool import EnhancedAgentTool

class EnhancedAgentTool(BaseTool):
    """Tool that delegates complex research tasks to the Enhanced Agent."""

    def __init__(self, enabled: bool = True):
        super().__init__(
            name="enhanced_research",
            description="Use for complex research, analysis, and information synthesis",
            enabled=enabled
        )

    async def execute(self, query: str) -> ToolResult:
        """Execute the enhanced agent on a research query."""
        try:
            from enhanced_agent.src.app import run_enhanced_agent

            # Run the enhanced agent
            result = await run_enhanced_agent(query)

            return ToolResult(
                output=result,
                success=True,
                metadata={"tool": "enhanced_research"}
            )

        except Exception as e:
            return ToolResult(
                output=f"Enhanced agent error: {str(e)}",
                success=False,
                error=str(e)
            )
```

### Using in OpenManus

```python
from OpenManus.app.agent.manus import Manus

async def main():
    # Initialize main agent (automatically includes enhanced agent tool)
    agent = Manus()

    # The agent will automatically use the enhanced tool for research queries
    result = await agent.run("What are the latest developments in quantum computing?")

    print(result)
```

### When to Use the Enhanced Agent

The enhanced agent is best suited for:

- **Research Queries** - Gathering and synthesizing information from multiple sources
- **Complex Analysis** - Breaking down multi-faceted problems
- **Creative Tasks** - Generating innovative solutions with supporting research
- **Decision Support** - Providing data-driven insights with confidence levels

The main agent handles:

- **Code Tasks** - Writing, debugging, refactoring code
- **File Operations** - Reading, writing, organizing files
- **Browser Automation** - Web scraping and interaction
- **Quick Queries** - Simple questions not requiring research

## 🔌 Custom MCP Servers

### Creating a Custom MCP Server

MCP servers provide external information to the agent. Here's how to create your own:

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def handle_query():
    """Handle incoming MCP queries."""
    data = request.json
    query = data.get('query', '')

    # Your custom logic here
    result = process_query(query)

    return jsonify({
        'result': result,
        'metadata': {
            'source': 'custom-mcp-server',
            'timestamp': datetime.now().isoformat()
        }
    })

def process_query(query: str) -> str:
    """Process the query and return results."""
    # Implement your logic:
    # - Database queries
    # - API calls
    # - Custom algorithms
    # - etc.
    return "Your results here"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### Configuring Custom MCP Server

Add your server to `enhanced_agent/config/mcp.json`:

```json
{
  "servers": {
    "my-custom-server": {
      "url": "http://localhost:8080",
      "model": null,
      "context_length": 4096,
      "temperature": 0.7,
      "timeout": 30,
      "max_retries": 3
    },
    "llama-mcp": {
      "url": "http://localhost:11434",
      "model": "gemma2:2b"
    }
  },
  "default_server": "my-custom-server"
}
```

### MCP Server Examples

#### Database Query Server

```python
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def query_database():
    query_text = request.json.get('query', '')

    # Convert natural language to SQL (simplified)
    sql = convert_to_sql(query_text)

    # Execute query
    conn = sqlite3.connect('mydata.db')
    cursor = conn.cursor()
    results = cursor.execute(sql).fetchall()
    conn.close()

    return jsonify({'result': format_results(results)})
```

#### API Aggregator Server

```python
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def aggregate_apis():
    query = request.json.get('query', '')

    # Query multiple APIs
    results = []
    results.append(query_api_1(query))
    results.append(query_api_2(query))
    results.append(query_api_3(query))

    # Combine and format results
    combined = combine_results(results)

    return jsonify({'result': combined})
```

## 🔗 API Integration

### Using the Enhanced Agent Programmatically

#### Async Python API

```python
import asyncio
from enhanced_agent.src.app import run_enhanced_agent

async def main():
    # Single query
    result = await run_enhanced_agent("What is quantum computing?")
    print(result)

    # Multiple queries
    queries = [
        "What is machine learning?",
        "How do neural networks work?",
        "What are the applications of AI?"
    ]

    results = await asyncio.gather(*[
        run_enhanced_agent(query) for query in queries
    ])

    for query, result in zip(queries, results):
        print(f"Q: {query}")
        print(f"A: {result}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

#### REST API Wrapper

Create a simple REST API wrapper:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enhanced_agent.src.app import run_enhanced_agent
import asyncio

app = FastAPI()

class Query(BaseModel):
    query: str
    user_id: str = "anonymous"

class Response(BaseModel):
    result: str
    query: str
    user_id: str

@app.post("/research", response_model=Response)
async def research(query: Query):
    """Research endpoint."""
    try:
        result = await run_enhanced_agent(query.query)
        return Response(
            result=result,
            query=query.query,
            user_id=query.user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Usage:

```bash
curl -X POST "http://localhost:8000/research" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is quantum computing?", "user_id": "user123"}'
```

#### Batch Processing

```python
import asyncio
import csv
from enhanced_agent.src.app import run_enhanced_agent

async def process_batch(input_file: str, output_file: str):
    """Process a batch of queries from CSV."""

    # Read queries
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        queries = [row['query'] for row in reader]

    # Process all queries concurrently
    results = await asyncio.gather(*[
        run_enhanced_agent(query) for query in queries
    ])

    # Write results
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['query', 'result'])
        writer.writeheader()
        for query, result in zip(queries, results):
            writer.writerow({'query': query, 'result': result})

    print(f"Processed {len(queries)} queries → {output_file}")

# Usage
asyncio.run(process_batch('queries.csv', 'results.csv'))
```

## 🧩 Extension Points

### Custom DSPy Modules

Extend the DSPy pipeline with custom modules:

```python
import dspy
from enhanced_agent.src.dspy_modules import QueryAnalysis

class CustomAnalysis(dspy.Signature):
    """Custom analysis signature."""
    query = dspy.InputField(desc="User query")
    domain = dspy.OutputField(desc="Query domain")
    complexity = dspy.OutputField(desc="Complexity level")
    custom_field = dspy.OutputField(desc="Your custom field")

class EnhancedPipeline(dspy.Module):
    """Enhanced pipeline with custom analysis."""

    def __init__(self):
        super().__init__()
        self.query_analysis = QueryAnalysis()
        self.custom_analysis = dspy.ChainOfThought(CustomAnalysis)

    def forward(self, query: str):
        # Standard analysis
        basic = self.query_analysis(query=query)

        # Custom analysis
        custom = self.custom_analysis(query=query)

        # Combine results
        return {
            **basic,
            'custom': custom
        }
```

### Custom Tools for OpenManus

Add your own tools to OpenManus:

```python
from OpenManus.app.tool.base import BaseTool, ToolResult

class MyCustomTool(BaseTool):
    """Your custom tool."""

    def __init__(self):
        super().__init__(
            name="my_tool",
            description="What your tool does",
            enabled=True
        )

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool."""
        try:
            # Your tool logic
            result = do_something(kwargs)

            return ToolResult(
                output=result,
                success=True,
                metadata={"tool": "my_tool"}
            )

        except Exception as e:
            return ToolResult(
                output=f"Error: {str(e)}",
                success=False,
                error=str(e)
            )

# Register tool
from OpenManus.app.tool.collection import ToolCollection

tool_collection = ToolCollection()
tool_collection.add_tool(MyCustomTool())
```

### Custom Response Formatters

Create custom output formats:

```python
from enhanced_agent.src.dspy_mcp_integration import DSPyMCPIntegration

class CustomFormatter:
    """Custom response formatter."""

    @staticmethod
    def format(result: dict) -> str:
        """Format result in custom way."""
        return f"""
# {result.get('title', 'Research Results')}

**Summary:** {result.get('summary', 'N/A')}

## Findings
{result.get('findings', 'No findings')}

## Recommendations
{result.get('recommendations', 'No recommendations')}

---
Generated: {result.get('timestamp', 'N/A')}
"""

# Use in your code
result = await run_research(query)
formatted = CustomFormatter.format(result)
print(formatted)
```

## 🧪 Testing Integration

### Integration Test Template

```python
import pytest
from OpenManus.app.agent.manus import Manus

@pytest.mark.integration
async def test_enhanced_agent_integration():
    """Test enhanced agent integration with OpenManus."""

    # Initialize agent
    agent = Manus()

    # Test research query delegation
    result = await agent.run(
        "Research the latest developments in quantum computing"
    )

    # Verify result structure
    assert "Direct Answer" in result or "direct answer" in result.lower()
    assert len(result) > 100  # Substantial response

@pytest.mark.integration
async def test_custom_mcp_server():
    """Test custom MCP server integration."""
    from enhanced_agent.src.enhanced_mcp_client import EnhancedMCPClient

    client = EnhancedMCPClient("config/mcp_custom.json")
    result = await client.query("test query", "my-custom-server")

    assert result is not None
    assert len(result) > 0
```

## 📚 Additional Resources

- [OpenManus Documentation](OpenManus/README.md)
- [Enhanced Agent Documentation](enhanced_agent/README.md)
- [DSPy Documentation](https://github.com/stanfordnlp/dspy)
- [MCP Specification](https://modelcontextprotocol.com)

---

**Questions?** Check the [main README](../README.md) or open an issue on GitHub.
