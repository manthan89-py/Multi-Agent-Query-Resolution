import asyncio
import os
from agno.agent import Agent
from agno.knowledge.website import WebsiteKnowledgeBase
from agno.vectordb.qdrant import Qdrant
from agno.tools.tavily import TavilyTools
from agno.embedder.mistral import MistralEmbedder
from agno.models.mistral import MistralChat
from dotenv import load_dotenv
from instructions import knowledge_agent_instructions
from response_model import ResponseOutput

load_dotenv()


COLLECTION_NAME = "website-content"
API_KEY = os.getenv("MISTRAL_API_KEY")

vector_db = Qdrant(
    embedder=MistralEmbedder(
        api_key=API_KEY,
        dimensions=1536,
    ),
    collection=COLLECTION_NAME,
    url="http://localhost:6333",
)

urls = [
    "https://www.infinitepay.io",
    "https://www.infinitepay.io/maquininha",
    "https://www.infinitepay.io/maquininha-celular",
    "https://www.infinitepay.io/tap-to-pay",
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
# Create a knowledge base with the seed URLs
knowledge_base = WebsiteKnowledgeBase(
    urls=urls,
    # Number of links to follow from the seed URLs
    max_links=5,
    # Table name: ai.website_documents
    vector_db=vector_db,
)

# Create an agent with the knowledge base
knowledge_agent = Agent(
    name="KnowledgeBase Agent",
    model=MistralChat(api_key=API_KEY, id=os.getenv("LLM_MODEL")),
    knowledge=knowledge_base,
    search_knowledge=True,
    instructions=knowledge_agent_instructions,
    debug_mode=True,
    tools=[TavilyTools(search="")],
)


# if __name__ == "__main__":
#     # Comment out after first run
#     asyncio.run(knowledge_base.aload(recreate=False))

#     # Create and use the agent
#     asyncio.run(knowledge_agent.aprint_response("What is infinitepay?", markdown=True))
