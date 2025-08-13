# 🎯 Usage Examples: Enhanced Research Agent

Based on your current setup (7/8 checks passed), here's exactly how to use the OpenManus + DSPy + MCP research agent.

## 🚀 Current System Status
- ✅ **Ollama**: Running with 3 models (gemma3:4b, qwen3:14b, gemma3:latest)
- ✅ **DSPy**: Installed and ready (will use fallback mode without OpenAI key)
- ✅ **MCP Client**: Configured for Ollama integration
- ✅ **OpenManus**: Ready for ReAct agent execution
- ⚠️ **OpenAI API**: Not configured (optional for enhanced DSPy performance)

## 🏃‍♂️ How to Run

### Option 1: Direct Run (Simplest)
```bash
cd /Users/raymondhunter/LocalProjects/03workspaceMar25/omd
python enhanced_agent/main.py
```

### Option 2: With OpenAI API (Best Performance)
```bash
export OPENAI_API_KEY="your-api-key-here"
python enhanced_agent/main.py
```

### Option 3: Demo Mode
```bash
python demo_agent.py
```

## 📱 What You'll See When Running

### Startup Screen
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

## 🗣️ Example Conversations

### Example 1: Technology Research
**You:** `What is machine learning?`

**Agent Processing:**
```
🧠 DSPy Query Analysis:
   Topic: machine learning
   Type: factual
   Search terms: machine learning, artificial intelligence, ML algorithms

🔍 MCP Query 1/3: 'machine learning'
   ✅ Got 1,234 characters of information
🔍 MCP Query 2/3: 'artificial intelligence'
   ✅ Got 987 characters of information
🔍 MCP Query 3/3: 'ML algorithms'
   ✅ Got 1,456 characters of information

🚀 Executing DSPy+MCP structured research pipeline...
✅ DSPy+MCP pipeline completed successfully
```

**Agent Response:**
```
## 🎯 Direct Answer
Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed for every task...

## 💡 Key Insights
- Supervised learning uses labeled data to train models
- Unsupervised learning finds patterns in unlabeled data
- Deep learning uses neural networks with multiple layers
- Applications span from recommendation systems to autonomous vehicles

## 📚 Supporting Information
Machine learning algorithms work by identifying patterns in training data...

## 🛠️ Next Steps
1. Start with basic concepts like linear regression
2. Practice with datasets on platforms like Kaggle
3. Learn Python libraries like scikit-learn and TensorFlow

---
**Research Analysis:** factual query about machine learning
**Confidence Level:** high - comprehensive information from multiple sources
```

### Example 2: Business Analysis
**You:** `How can a small restaurant improve customer retention?`

**Agent Response:**
```
## 🎯 Direct Answer
Small restaurants can improve customer retention through personalized service, loyalty programs, consistent quality, and community engagement strategies...

## 💡 Key Insights
- Loyalty programs can increase repeat visits by 35%
- Personal recognition of regular customers builds emotional connection
- Social media engagement creates community around the restaurant
- Consistent food quality is the foundation of customer retention

## 🛠️ Next Steps
1. Implement a simple points-based loyalty program
2. Train staff to remember regular customers' preferences
3. Create engaging social media content showcasing daily specials
4. Collect customer feedback through digital surveys

---
**Research Analysis:** analytical query about restaurant customer retention
**Confidence Level:** high - practical strategies identified
```

### Example 3: Creative Problem Solving
**You:** `Design an eco-friendly office building for the future`

**Agent Response:**
```
## 🎯 Direct Answer
A future eco-friendly office building should integrate renewable energy systems, biophilic design, smart building technologies, and circular economy principles...

## 💡 Key Insights
- Living walls can reduce air conditioning needs by 15%
- Smart glass automatically adjusts for optimal natural lighting
- Rainwater harvesting systems can provide 40% of water needs
- Modular design allows for easy reconfiguration and expansion

## 🛠️ Next Steps
1. Conduct site analysis for solar potential and wind patterns
2. Design integrated systems for energy, water, and waste management
3. Plan flexible spaces that can adapt to changing work patterns
4. Select sustainable materials with low environmental impact

---
**Research Analysis:** creative query about eco-friendly office design
**Confidence Level:** medium - innovative concepts require further validation
```

## 🎮 Interactive Usage Patterns

### Quick Fact-Finding
- `What is quantum computing?`
- `How does photosynthesis work?`
- `What are the latest developments in renewable energy?`

### Analysis & Strategy
- `How can businesses prepare for economic uncertainty?`
- `What are the pros and cons of remote work?`
- `Analyze the impact of AI on healthcare`

### Creative & Planning
- `Design a sustainable transportation system for cities`
- `Create a learning plan for data science`
- `Plan a zero-waste lifestyle transition`

### Problem Solving
- `My startup needs to reduce costs - what options do I have?`
- `How can schools improve student engagement?`
- `What are innovative solutions for food waste?`

## 🛠️ Advanced Usage Tips

### 1. Multi-Step Queries
You can ask follow-up questions in the same session:
```
You: What is blockchain?
Agent: [provides comprehensive blockchain explanation]

You: How is it used in supply chain management?
Agent: [builds on previous context for supply chain applications]
```

### 2. Specific Context Requests
Be specific about what you need:
- `Explain quantum computing for a business audience`
- `Give me technical details about machine learning algorithms`
- `Focus on practical applications of renewable energy`

### 3. Problem-Solving Framework
For complex problems, structure your query:
- `Problem: High employee turnover. Industry: Tech startup. Budget: Limited. Please analyze and provide solutions.`

## 🔧 Troubleshooting Usage

### If DSPy Integration Fails
The agent will fall back to basic MCP mode:
```
⚠️  DSPy structured reasoning: DISABLED (using basic MCP)
📊 Available MCP servers: ['llama-mcp']
```

### If MCP Connection Fails
Check Ollama is running:
```bash
curl http://localhost:11434/api/version
# Should return: {"version":"0.11.4"}
```

### If OpenManus Config Issues
The agent may show configuration warnings. Most functionality will still work.

## 🎉 Ready to Start!

Your enhanced research agent is ready to help with:
- **Research**: Get comprehensive, structured information on any topic
- **Analysis**: Break down complex problems with systematic thinking  
- **Planning**: Create actionable strategies with supporting research
- **Decision Support**: Get data-driven insights with confidence levels

Just run `python enhanced_agent/main.py` and start asking questions! 🚀