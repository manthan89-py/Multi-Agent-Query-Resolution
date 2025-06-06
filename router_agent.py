import asyncio
import os
from agno.team.team import Team
from agno.models.mistral import MistralChat
from dotenv import load_dotenv
from customer_support_agent import customer_support_agent
from knowledge_agent import knowledge_agent, knowledge_base
from instructions import router_agent_instructions
from pydantic import BaseModel, Field


class AgentWorkflow(BaseModel):
    agent_name: str = Field(description="Name of the agent")
    tool_calls: dict = Field(description="Tool calls for the agent")


class ResponseOutput(BaseModel):
    reponse: str = Field(description="Response from the agent")
    source_agent_response: str = Field(description="Response from the source agent")
    agent_workflow: AgentWorkflow = Field(description="Agent workflow")


load_dotenv()

customer_support_product_inquiry_team = Team(
    name="Customer Support and Product Inquiry Team",
    mode="route",
    model=MistralChat(id=os.getenv("LLM_MODEL")),
    members=[
        customer_support_agent,
        knowledge_agent,
    ],
    markdown=True,
    instructions=router_agent_instructions,
    show_members_responses=True,
)

if __name__ == "__main__":
    input_query = str(input("Enter your query: "))
    # asyncio.run(knowledge_base.aload(recreate=True))
    asyncio.run(
        customer_support_product_inquiry_team.aprint_response(input_query, stream=True)
    )
