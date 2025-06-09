# workflow.py

from agno.workflow import Workflow, RunEvent, RunResponse
from textwrap import dedent
from router_agent import customer_support_product_inquiry_team as router_agent_team
from typing import Dict, Iterator, Optional
from agno.agent import Agent
from instructions import personality_agent_instructions
from models import PersonalityLayerResponse, FinalResponseOutput
from agno.storage.json import JsonStorage
from agno.models.mistral import MistralChat
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")


class IntelligentQueryResolver(Workflow):
    description: str = dedent(
        """
        This workflow resolves customer queries by routing them to the most appropriate agent and finally answering the query with Personality AI.
        """
    )

    personality_layer: Agent = Agent(
        name="Personality AI",
        model=MistralChat(api_key=API_KEY, id=os.getenv("LLM_MODEL")),
        description="Personality AI",
        tools=[],
        instructions=personality_agent_instructions,
        response_model=PersonalityLayerResponse,
        debug_mode=True,
    )

    def run(self, query: str) -> RunResponse:
        # Route the query to the most appropriate agent
        team_response = router_agent_team.run(query)
        # if team_response.status == RunEvent.SUCCESS:
        #     # pass the AI response to the Personality AI agent
        team_response_data = team_response.content.model_dump()
        peronsality_ai_response = self.personality_layer.run(
            team_response_data.get("response"),
        )
        source_agent_response = peronsality_ai_response.content.response
        # Swapping the response and source_agent_response
        team_response_data["response"], team_response_data["source_agent_response"] = (
            source_agent_response,
            team_response_data["response"],
        )

        # Workflow is completed
        return RunResponse(
            content=FinalResponseOutput(**team_response_data),
            event=RunEvent.workflow_completed,
        )


# if __name__ == "__main__":
#     workflow = IntelligentQueryResolver(storage=JsonStorage("tmp/workflow_data.json"))
#     response = workflow.run(query="What is infinitepay?")
#     print(response.content)
