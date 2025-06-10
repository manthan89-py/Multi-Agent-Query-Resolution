# agents/knowledge_agent.py

"""Knowledge base agent for handling product information and general inquiries.
This module creates an intelligent agent that can search through InfinitePay's
website content and external sources to answer product-related questions.
"""

import os
from typing import List

from agno.agent import Agent
from agno.knowledge.website import WebsiteKnowledgeBase
from agno.tools.tavily import TavilyTools
from agno.embedder.mistral import MistralEmbedder
from agno.models.mistral import MistralChat
from agno.vectordb.chroma import ChromaDb
from dotenv import load_dotenv

from utils import knowledge_agent_instructions, AgentResponseOutput, get_logger

# Configure logging
logger = get_logger(__name__)

# Load environment variables
load_dotenv()

# Configuration
COLLECTION_NAME = "infinitepay-extracted-content"
API_KEY = os.getenv("MISTRAL_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral-large-latest")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable is required")

# InfinitePay website URLs for knowledge extraction
INFINITEPAY_URLS: List[str] = [
    "https://www.infinitepay.io",
    # "https://www.infinitepay.io/maquininha",
    # "https://www.infinitepay.io/maquininha-celular",
    # "https://www.infinitepay.io/tap-to-pay",
    "https://www.infinitepay.io/pdv",
    "https://www.infinitepay.io/receba-na-hora",
    "https://www.infinitepay.io/gestao-de-cobranca-2",
    "https://www.infinitepay.io/gestao-de-cobranca",
    "https://www.infinitepay.io/link-de-pagamento",
    "https://www.infinitepay.io/loja-online",
    "https://www.infinitepay.io/boleto",
    "https://www.infinitepay.io/conta-digital",
    "https://www.infinitepay.io/conta-pj",
    "https://www.infinitepay.io/pix",
    "https://www.infinitepay.io/pix-parcelado",
    "https://www.infinitepay.io/emprestimo",
    "https://www.infinitepay.io/cartao",
    "https://www.infinitepay.io/rendimento",
]


def create_vector_db() -> ChromaDb:
    """
    Create and configure the ChromaDB vector database for knowledge storage.

    Returns:
        ChromaDb: Configured vector database instance

    Raises:
        Exception: If vector database creation fails
    """
    try:
        vector_db = ChromaDb(
            collection=COLLECTION_NAME,
            embedder=MistralEmbedder(api_key=API_KEY),
            persistent_client=True,
            path="storage/chroma_db",
        )
        logger.info(f"Vector database initialized with collection: {COLLECTION_NAME}")
        return vector_db
    except Exception as e:
        logger.error(f"Failed to create vector database: {str(e)}")
        raise


def create_knowledge_base(vector_db: ChromaDb) -> WebsiteKnowledgeBase:
    """
    Create the website knowledge base with InfinitePay content.

    Args:
        vector_db: The vector database instance to use for storage

    Returns:
        WebsiteKnowledgeBase: Configured knowledge base instance

    Raises:
        Exception: If knowledge base creation fails
    """
    try:
        knowledge_base = WebsiteKnowledgeBase(
            urls=INFINITEPAY_URLS,
            num_documents=4,
            max_links=1,
            max_depth=1,
            vector_db=vector_db,
        )
        logger.info(f"Knowledge base created with {len(INFINITEPAY_URLS)} URLs")
        return knowledge_base
    except Exception as e:
        logger.error(f"Failed to create knowledge base: {str(e)}")
        raise


def create_knowledge_agent(knowledge_base: WebsiteKnowledgeBase) -> Agent:
    """
    Create and configure the knowledge agent.

    Args:
        knowledge_base: The knowledge base instance to use

    Returns:
        Agent: Configured knowledge agent instance

    Raises:
        Exception: If agent creation fails
    """
    try:
        # Initialize tools
        tools = []
        if TAVILY_API_KEY:
            tools.append(TavilyTools(search=""))
            logger.info("Tavily search tool enabled")
        else:
            logger.warning("TAVILY_API_KEY not found, web search disabled")

        agent = Agent(
            name="KnowledgeBase Agent",
            model=MistralChat(api_key=API_KEY, id=LLM_MODEL),
            knowledge=knowledge_base,
            search_knowledge=True,
            instructions=knowledge_agent_instructions,
            debug_mode=True,
            tools=tools,
            response_model=AgentResponseOutput,
        )
        logger.info("Knowledge agent initialized successfully")
        return agent
    except Exception as e:
        logger.error(f"Failed to create knowledge agent: {str(e)}")
        raise


# Initialize components
try:
    vector_db = create_vector_db()
    knowledge_base = create_knowledge_base(vector_db)
    knowledge_agent = create_knowledge_agent(knowledge_base)
except Exception as e:
    logger.error(f"Failed to initialize knowledge agent components: {str(e)}")
    raise
