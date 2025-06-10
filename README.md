# Multi-Agent Customer Query Resolution System

A sophisticated multi-agent system designed to handle customer queries related to InfinitePay services through intelligent routing and specialized agent responses.

## 🤖 Agent Overview

### 1. Router Agent
- **Purpose**: Main orchestration agent that analyzes incoming queries
- **Function**: Routes queries to appropriate specialized agents based on content analysis
- **Technology**: Built using Agno Framework's Team and Workflow components

### 2. Product Knowledge Specialist
- **Purpose**: Handles InfinitePay product-related inquiries
- **Knowledge Source**: Vector database (ChromaDB) containing InfinitePay documentation
- **Process**: 
  - Generates efficient embedding queries using LLM
  - Retrieves most relevant chunks from vector database
  - Provides accurate product information

### 3. Customer Support Agent
- **Purpose**: Assists with customer issues and support requests
- **Capabilities**:
  - Accesses customer information from database
  - Reviews previous interaction history
  - Creates support tickets when necessary
  - Provides personalized solutions

### 4. Personality Layer
- **Purpose**: Final response enhancement layer
- **Function**: Transforms technical responses into human-friendly, conversational format
- **Benefit**: Improves user experience and engagement

## 📋 Response Format

The system returns structured responses using Pydantic models:

```json
{
  "response": "Enhanced human-friendly response from Personality Layer",
  "source_agent_response": "Raw response from the originating agent",
  "agent_workflow": {
    "agent_name": "product_knowledge_specialist | customer_support_agent",
    "tool_calls": {
      "tool_name": "parameters_and_metadata"
    }
  }
}
```

## 🛠️ Technology Stack

- **Framework**: Agno Framework for agent orchestration
- **API**: FastAPI with Uvicorn server
- **Vector Database**: ChromaDB for efficient similarity search
- **Knowledge Base**: WebSiteKnowledgeBase for chunk retrieval
- **LLM Integration**: Mistral API for natural language processing
- **Search Enhancement**: Tavily API for additional context
- **Validation**: Pydantic models for response structure

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Docker (optional)
- Mistral API Key
- Tavily API Key

### 📦 Installation Methods

#### Method 1: Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/manthan89-py/Multi-Agent-Query-Resolution.git
   cd <directory>
   ```

2. **Environment Setup**
   ```bash
   # Rename environment file
   cp .env.example .env
   
   # Edit .env file with your API keys
   MISTRAL_API_KEY=your_mistral_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

3. **Virtual Environment Setup**
   ```bash
   # Create virtual environment using uv
   uv venv --python=3.11
   
   # Activate virtual environment
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate     # Windows
   ```

4. **Install Dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```

5. **Run the Application**
   ```bash
   python api.py
   ```

#### Method 2: Docker Setup (Recommended - Make sure you have Docker installed)

1. **Build Docker Image**
   ```bash
   make build
   ```

2. **Run Docker Container**
   ```bash
   make run
   ```

3. **View Available Commands**
   ```bash
   make help
   ```

### 🌐 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- ```Make sure to run /load_datababse first to populate the database.```

## 🎯 Key Features

- **Intelligent Routing**: Automatically directs queries to the most appropriate agent
- **RAG Pipeline**: Efficient retrieval-augmented generation for accurate responses
- **Customer Context**: Leverages customer history for personalized support
- **Scalable Architecture**: Built with Agno framework for easy agent addition
- **Human-Friendly Output**: Personality layer ensures natural conversation flow
- **Structured Responses**: Consistent JSON output format for easy integration

## 📁 Project Structure

```
multi-agent-customer-resolution/
├── api.py                 # FastAPI application entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── Dockerfile            # Docker configuration
├── Makefile             # Build and run commands
├── results.json         # Sample responses for testing
├── agents/              # Agent implementations
│   ├── router.py       # Router agent
│   ├── knowledge_agent.py  # Product knowledge agent
│   ├── customer_support_agent.py  # Customer support agent
│   └── workflow.py  # Workflow orchestration 
└── utils/                  
    ├── instructions.py     # Prompts
    ├── logger.py            # logging functions
    └── models.py           # Data/Response models
```

## 🧪 Testing

Sample results and test cases are available in `results.json`. This file contains:
- Example queries
- Expected responses
- Agent workflow traces

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MISTRAL_API_KEY` | API key for Mistral LLM service | Yes |
| `TAVILY_API_KEY` | API key for Tavily search service | Yes |
| `CHROMA_DB_PATH` | Path to ChromaDB storage | No |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARN, ERROR) | No |

### Customization Options

- **Add New Agents**: Extend the system by implementing new agent classes
- **Modify Routing Logic**: Update router agent for different query categorization
- **Enhance Knowledge Base**: Add more documents to the vector database
- **Customize Personality**: Adjust the personality layer for different brand voices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-agent`)
3. Commit your changes (`git commit -am 'Add new agent functionality'`)
4. Push to the branch (`git push origin feature/new-agent`)
5. Create a Pull Request

## 📝 API Usage Examples

### Basic Query
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the fees of the Maquininha Smart",
    "user_id": "client789"
    }'
```

### Response Example
```json
    {
        "response": "Sure thing! You can get the Maquininha Smart on a payment plan of 12 installments of R$ 16.58 each. Just a heads-up, the tax rates vary based on how you pay and your monthly revenue. For debit transactions, the tax starts at 1.37%. If you're paying with credit in one go, it's 3.15%, and if you split it into 12 installments, the rate is 12.40%. Oh, and Pix transactions? No tax at all! The good news is, the more you earn monthly, the lower these rates get. For all the nitty-gritty details, you can check out InfinitePay's official website. I'd be happy to help with any other questions you might have!",
        "source_agent_response": "The Maquininha Smart is available for a payment plan of 12 installments of R$ 16.58. Different tax rates apply depending on the payment method and monthly revenue. For example, for debit transactions, the tax rate starts at 1.37%, while for credit transactions paid in one installment, the rate starts at 3.15%, and for 12 installments, it is 12.40%. Pix transactions have a tax rate of zero. The tax rates decrease as the monthly revenue increases. For more detailed information, you can refer to the official website of InfinitePay.",
        "agent_workflow": {
            "agent_name": "Product Knowledge Specialist",
            "tool_calls": {
                "search_knowledge_base": [
                    {
                        "query": "fees of the Maquininha Smart"
                    }
                ]
            }
        }
    }
```

## 🐛 Troubleshooting

### Common Issues

1. **API Keys Not Working**
   - Ensure `.env` file is properly configured
   - Verify API keys are valid and have sufficient quota

2. **Vector Database Issues**
   - Check ChromaDB installation and permissions
   - Verify knowledge base is properly indexed

3. **Agent Routing Problems**
   - Review router agent logic
   - Check query classification accuracy

### Getting Help

- Check the API documentation at `/docs`
- Review sample responses in `results.json`
- Enable debug logging for detailed troubleshooting

## 🔮 Future Enhancements

- Multi-language support
- Voice query processing
- Advanced analytics dashboard
- Integration with more knowledge sources
- Real-time learning capabilities

---

**Built with ❤️ using Agno Framework, FastAPI, and ChromaDB**