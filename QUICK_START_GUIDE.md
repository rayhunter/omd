# 🚀 Quick Start Guide: OpenManus + DSPy + MCP Research Agent

This guide shows you how to run and use the enhanced research agent that combines three powerful AI technologies.

## 📋 Prerequisites

### 1. Python Environment
```bash
# Ensure Python 3.8+ is installed
python --version

# Optional: Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
# Install the enhanced agent package
cd enhanced_agent
pip install -e .

# Install DSPy for structured reasoning
pip install dspy-ai

# Install OpenManus dependencies  
cd ../OpenManus
pip install -r requirements.txt

```

### 3. Set Up Ollama (for MCP)
```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# In another terminal, pull a model
ollama pull gemma2:2b  # or any other model
```

### 4. Optional: Configure OpenAI API (for best DSPy performance)
```bash
# Set your OpenAI API key for DSPy structured reasoning
export OPENAI_API_KEY="your-api-key-here"
```

## 🏃‍♂️ Running the Application

### Method 1: Full Integration (Recommended)
```bash
# From the main directory
python enhanced_agent/main.py
streamlit run enhanced_agent_streamlit.py --server.headless true --server.port 8501
```

### Method 2: Alternative Entry Point
```bash
# From the main directory  
python enhanced_agent/src/app.py
```

### Method 3: Test Components First
```bash
# Test DSPy integration without OpenManus dependencies
python test_dspy_standalone.py
```

## 💬 Using the Research Agent

Once running, you'll see something like:

```
🚀 Enhanced Research Agent - OpenManus + DSPy + MCP Integration
✅ DSPy+MCP structured reasoning: ENABLED
📊 Available MCP servers: ['llama-mcp']
🎯 Default MCP server: llama-mcp
--------------------------------------------------
This agent combines:
1. 🤖 OpenManus ReAct pattern for step-by-step processing
2. 🧠 DSPy structured reasoning for query analysis and response generation
3. 🔍 MCP for real-time information gathering
4. 📊 Structured pipeline: Query Analysis → Information Gathering → Synthesis → Response
--------------------------------------------------

Enter your request (or 'quit' to exit):
```

### Example Usage Sessions

#### 🔬 **Research Query Example**
```
Enter your request: What are the latest developments in quantum computing?

🧠 DSPy Query Analysis:
   Topic: quantum computing developments
   Type: factual
   Search terms: quantum computing, latest developments, quantum supremacy, quantum algorithms

🔍 MCP Query 1/3: 'quantum computing'
   ✅ Got 1247 characters of information
🔍 MCP Query 2/3: 'latest developments'  
   ✅ Got 892 characters of information
🔍 MCP Query 3/3: 'quantum supremacy'
   ✅ Got 1056 characters of information

🚀 Executing DSPy+MCP structured research pipeline...
✅ DSPy+MCP pipeline completed successfully

## 🎯 Direct Answer
Quantum computing has seen significant breakthroughs in 2024, with major advances in error correction, quantum algorithms, and practical applications...

## 💡 Key Insights  
- IBM achieved a major milestone with their 1000-qubit processor
- Google demonstrated quantum advantage in optimization problems
- Commercial applications emerging in cryptography and drug discovery

## 📚 Supporting Information
Recent developments include improvements in quantum error correction rates...

## 🛠️ Next Steps
- Monitor developments in quantum error correction
- Explore potential applications in your field
- Consider partnerships with quantum computing companies

---
**Research Analysis:** factual query about quantum computing developments
**Confidence Level:** high - comprehensive information gathered from multiple sources
```

#### 🤔 **Analytical Query Example**
```
Enter your request: How can small businesses benefit from AI automation?

📊 Query Analysis Complete - Topic: AI automation for small businesses, Type: analytical

🚀 Executing DSPy+MCP structured research pipeline...

## 🎯 Direct Answer
Small businesses can significantly benefit from AI automation through cost reduction, improved efficiency, and enhanced customer experience...

## 💡 Key Insights
- 67% cost reduction in routine tasks through automation
- Customer service chatbots can handle 80% of common inquiries  
- Predictive analytics helps optimize inventory and cash flow

## 🛠️ Next Steps
1. Identify repetitive tasks suitable for automation
2. Start with low-risk, high-impact areas like customer service
3. Gradually expand to inventory management and marketing automation
```

#### ❓ **Creative Query Example**
```
Enter your request: Design a sustainable city planning strategy for the next 50 years

📊 Query Analysis Complete - Topic: sustainable city planning, Type: creative

## 🎯 Direct Answer
A comprehensive 50-year sustainable city strategy should integrate smart infrastructure, renewable energy systems, and community-centered design...

## 💡 Key Insights
- Vertical farming reduces land use by 95% while increasing yield
- Smart grids can reduce energy consumption by 30-40%
- Mixed-use development reduces transportation needs by 25%

## 🛠️ Next Steps
1. Conduct community stakeholder workshops
2. Develop phased implementation timeline
3. Secure funding through green bonds and public-private partnerships
```

## 🔧 Configuration Options

### MCP Server Configuration
Edit `enhanced_agent/config/mcp.json`:
```json
{
  "servers": {
    "llama-mcp": {
      "url": "http://localhost:11434",
      "model": "gemma2:2b",
      "context_length": 4096,
      "temperature": 0.7,
      "max_tokens": 2048
    }
  },
  "default_server": "llama-mcp"
}
```

### DSPy Model Configuration
In the code, you can modify `enhanced_agent/src/dspy_mcp_integration.py`:
```python
# Change the LLM model for DSPy
dspy_mcp = DSPyMCPIntegration(
    llm_model="gpt-4",  # or "gpt-3.5-turbo", "claude-3-sonnet", etc.
    dspy_cache=True
)
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. **"DSPy+MCP integration failed to initialize"**
```bash
# Install DSPy
pip install dspy-ai>=2.0.0

# Set OpenAI API key (optional)
export OPENAI_API_KEY="your-key-here"
```

#### 2. **"MCP query failed" or "Error: Could not connect to Llama MCP server"**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# If not running:
ollama serve

# Pull a model if needed:
ollama pull gemma2:2b
```

#### 3. **"OpenManus configuration error"**  
```bash
# Check OpenManus config
cat OpenManus/config/config.toml

# Copy example if needed:
cp OpenManus/config/config.example.toml OpenManus/config/config.toml
```

#### 4. **Import errors**
```bash
# Install all dependencies
pip install -r enhanced_agent/requirements.txt
pip install -r OpenManus/requirements.txt

# Install packages in development mode
cd enhanced_agent && pip install -e .
cd ../OpenManus && pip install -e .
```

## 📊 Understanding the Output

The agent provides structured responses with:

- **🎯 Direct Answer**: Immediate response to your question
- **💡 Key Insights**: Most important findings from the research
- **📚 Supporting Information**: Detailed background and context  
- **🛠️ Next Steps**: Actionable recommendations
- **📈 Research Metadata**: Query analysis, confidence levels, and information gaps

## 🎮 Advanced Usage

### Batch Processing
```bash
# Create a file with queries
echo "What is machine learning?" > queries.txt  
echo "How do neural networks work?" >> queries.txt

# Process multiple queries (create a simple script)
while IFS= read -r query; do
    echo "Processing: $query"
    python -c "
import asyncio
from enhanced_agent.src.app import run_enhanced_agent
result = asyncio.run(run_enhanced_agent('$query'))
print(result)
print('='*50)
"
done < queries.txt
```

### API Usage (Programmatic)
```python
import asyncio
from enhanced_agent.src.app import run_enhanced_agent

async def research_question(question):
    result = await run_enhanced_agent(question)
    return result

# Use in your own applications
answer = asyncio.run(research_question("What is the future of renewable energy?"))
print(answer)
```

## 🎉 You're Ready!

The research agent is now ready to help you with:
- **Research queries**: Get comprehensive information on any topic
- **Analysis tasks**: Break down complex problems with structured thinking
- **Creative challenges**: Generate innovative solutions with supporting research
- **Decision support**: Get data-driven insights with actionable recommendations

Type your questions and watch the magic of OpenManus + DSPy + MCP integration in action! 🚀