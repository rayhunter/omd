# Enhanced Agent Integration

This document explains how the enhanced agent is integrated with the main OpenManus application and how to test the integration.

## Overview

The enhanced agent has been integrated into OpenManus as a tool, allowing the main agent to delegate complex tasks to it when needed. This combines the strengths of both agents:

- **OpenManus Agent**: General-purpose agent with tools for coding, file operations, and web browsing
- **Enhanced Agent**: Specialized in research, complex reasoning, and information synthesis

## How It Works

1. The `EnhancedAgentTool` class acts as a bridge between the main agent and the enhanced agent
2. When the main agent encounters a task that would benefit from the enhanced agent's capabilities, it can delegate to it
3. The enhanced agent processes the task and returns the results to the main agent

## Testing the Integration

### Prerequisites

1. Ensure both packages are installed in development mode:
   ```bash
   # From the project root
   cd OpenManus
   pip install -e .
   cd ../enhanced_agent
   pip install -e .
   cd ..
   ```

2. Install test dependencies:
   ```bash
   pip install pytest pytest-asyncio
   ```

### Running the Integration Test

1. **Run the test script**:
   ```bash
   python scripts/test_enhanced_agent_integration.py
   ```

   This will test several queries that benefit from the enhanced agent's capabilities.

2. **Manual Testing**:
   You can also test the integration manually by running the main agent and using queries that would trigger the enhanced agent:
   ```bash
   cd OpenManus
   python -m main
   ```
   
   Try queries like:
   - "Research the latest developments in quantum computing"
   - "What are the current best practices for fine-tuning large language models?"
   - "Analyze the impact of AI on healthcare in 2025"

## How to Use the Enhanced Agent in Code

To use the enhanced agent in your code:

```python
from OpenManus.app.agent.manus import Manus

async def run_agent(query):
    agent = Manus()
    result = await agent.run(query)
    return result

# Example usage
result = asyncio.run(run_agent("Your research query here"))
print(result)
```

## Troubleshooting

1. **Import Errors**:
   - Ensure both packages are installed in development mode
   - Check that the Python path includes the project root

2. **Agent Not Being Used**:
   The main agent will only delegate to the enhanced agent for certain types of queries. If you want to force its use, you can modify the prompt to explicitly mention using the enhanced agent.

3. **Performance Issues**:
   The enhanced agent might be slower than the main agent for simple tasks due to its more sophisticated processing.

## Development Notes

- The integration is designed to be non-disruptive - the enhanced agent is just another tool in the main agent's toolbox
- The enhanced agent can be enabled/disabled via the `enabled` flag in the `EnhancedAgentTool` class
- All interactions with the enhanced agent are logged for debugging purposes
