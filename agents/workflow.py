# agents/workflow.py
"""
Main workflow orchestrator for the intelligent query resolution system.

This module defines the primary workflow that coordinates multiple agents
to resolve customer queries through routing and personality enhancement.
"""

import os
import logging
from textwrap import dedent
from typing import Optional

from agno.workflow import Workflow, RunEvent, RunResponse
from agno.agent import Agent
from agno.models.mistral import MistralChat
from agno.storage.json import JsonStorage
from dotenv import load_dotenv

from agents import router_agent_team
from utils import personality_agent_instructions, PersonalityLayerResponse, FinalResponseOutput

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("MISTRAL_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral-large-latest")

if not API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable is required")


class IntelligentQueryResolver(Workflow):
    """
    Main workflow class that resolves customer queries by routing them to the
    most appropriate agent and applying a personality layer for final response.

    This workflow coordinates multiple specialized agents to provide comprehensive
    customer support and product information responses.
    """

    description: str = dedent(
        """
        This workflow resolves customer queries by routing them to the most appropriate agent 
        and finally answering the query with Personality AI for enhanced user experience.
        
        The workflow consists of:
        1. Query routing to specialized agents (customer support or knowledge base)
        2. Response processing and enhancement through personality layer
        3. Final response compilation with workflow tracking
        """
    )

    def __init__(self, storage: Optional[JsonStorage] = None, **kwargs):
        """
        Initialize the workflow with optional storage backend.

        Args:
            storage: Optional JSON storage for workflow persistence
            **kwargs: Additional workflow configuration parameters
        """
        super().__init__(storage=storage, **kwargs)
        self._initialize_personality_layer()

    def _initialize_personality_layer(self) -> None:
        """Initialize the personality AI agent for response enhancement."""
        try:
            self.personality_layer = Agent(
                name="Personality AI",
                model=MistralChat(api_key=API_KEY, id=LLM_MODEL),
                description="AI agent that adds conversational personality and warmth to responses",
                tools=[],
                instructions=personality_agent_instructions,
                response_model=PersonalityLayerResponse,
                debug_mode=True,
            )
            logger.info("Personality layer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize personality layer: {str(e)}")
            raise

    def run(self, query: str) -> RunResponse:
        """
        Execute the complete workflow to resolve a customer query.

        Args:
            query: The customer query to be processed

        Returns:
            RunResponse: The workflow response containing the final output

        Raises:
            Exception: If any step in the workflow fails
        """
        try:
            # Input validation
            if not query or not query.strip():
                raise ValueError("Query cannot be empty")

            query = query.strip()
            logger.info(f"Starting workflow for query: {query[:100]}...")

            # Step 1: Route the query to the most appropriate agent
            logger.info("Routing query to appropriate agent team...")
            team_response = router_agent_team.run(query)

            if not team_response or not team_response.content:
                raise RuntimeError("Router team failed to generate response")

            # Extract team response data
            team_response_data = team_response.content.model_dump()
            logger.info(
                f"Router team response received from: {team_response_data.get('agent_workflow', {}).get('agent_name', 'Unknown')}"
            )

            # Step 2: Apply personality layer enhancement
            logger.info("Applying personality layer enhancement...")
            original_response = team_response_data.get("response", "")

            if not original_response:
                raise RuntimeError("No response received from routing team")

            personality_response = self.personality_layer.run(original_response)

            if not personality_response or not personality_response.content:
                raise RuntimeError("Personality layer failed to generate response")

            # Step 3: Prepare final response with proper structure
            enhanced_response = personality_response.content.response
            logger.info("Personality enhancement completed successfully")

            # Swap responses: enhanced becomes primary, original becomes source
            team_response_data.update(
                {
                    "response": enhanced_response,
                    "source_agent_response": original_response,
                }
            )

            # Create final response
            final_response = FinalResponseOutput(**team_response_data)

            logger.info("Workflow completed successfully")
            return RunResponse(
                content=final_response,
                event=RunEvent.workflow_completed,
            )

        except ValueError as e:
            logger.error(f"Validation error in workflow: {str(e)}")
            return RunResponse(
                content=None,
                event=RunEvent.workflow_failed,
                messages=[f"Validation error: {str(e)}"],
            )
        except RuntimeError as e:
            logger.error(f"Runtime error in workflow: {str(e)}")
            return RunResponse(
                content=None,
                event=RunEvent.workflow_failed,
                messages=[f"Workflow error: {str(e)}"],
            )
        except Exception as e:
            logger.error(f"Unexpected error in workflow: {str(e)}", exc_info=True)
            return RunResponse(
                content=None,
                event=RunEvent.workflow_failed,
                messages=[f"Unexpected error: {str(e)}"],
            )

    def health_check(self) -> bool:
        """
        Perform a health check on the workflow components.

        Returns:
            bool: True if all components are healthy, False otherwise
        """
        try:
            # Check if personality layer is initialized
            if not hasattr(self, "personality_layer") or self.personality_layer is None:
                logger.error("Personality layer not initialized")
                return False

            # Check if router team is available
            if router_agent_team is None:
                logger.error("Router agent team not available")
                return False

            logger.info("Workflow health check passed")
            return True

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
