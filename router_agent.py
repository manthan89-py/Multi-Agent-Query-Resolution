# router_agent.py
"""
Router agent team configuration for routing queries to appropriate specialists.

This module sets up a team of agents that can handle customer support and
product inquiry requests by routing them to the most suitable agent.
"""

import os
import logging
from typing import List

from agno.team.team import Team
from agno.models.mistral import MistralChat
from dotenv import load_dotenv

from customer_support_agent import customer_support_agent
from knowledge_agent import knowledge_agent
from instructions import router_agent_instructions
from models import AgentResponseOutput

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "mistral-large-latest")
API_KEY = os.getenv("MISTRAL_API_KEY")

if not API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable is required")


def create_customer_support_team() -> Team:
    """
    Create and configure the customer support and product inquiry team.

    Returns:
        Team: Configured team instance with routing capabilities

    Raises:
        Exception: If team creation fails
    """
    try:
        team = Team(
            name="Customer Support and Product Inquiry Team",
            mode="route",
            model=MistralChat(api_key=API_KEY, id=LLM_MODEL),
            members=[
                customer_support_agent,
                knowledge_agent,
            ],
            markdown=True,
            instructions=router_agent_instructions,
            show_members_responses=True,
            response_model=AgentResponseOutput,
        )
        logger.info("Customer support team initialized successfully")
        return team
    except Exception as e:
        logger.error(f"Failed to create customer support team: {str(e)}")
        raise


# Create the team instance
customer_support_product_inquiry_team = create_customer_support_team()
