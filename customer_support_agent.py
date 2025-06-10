# customer_support_agent.py
"""
Customer support agent implementation for handling support tickets and customer inquiries.

This module provides functionality to create support tickets, lookup customer information,
and check ticket status through a conversational AI agent interface.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from agno.agent import Agent
from agno.models.mistral import MistralChat
from dotenv import load_dotenv

from instructions import customer_support_agent_instructions
from models import AgentResponseOutput

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("MISTRAL_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral-large-latest")

if not API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable is required")

# In-memory storage for demo purposes
# Note: In production, use a proper database
TICKETS: Dict[str, Dict[str, Any]] = {}
TICKET_COUNTER = 1000

# Mock customer database
# Note: In production, this would be replaced with actual database queries
CUSTOMERS: Dict[str, Dict[str, Any]] = {
    "john@example.com": {
        "name": "John Silva",
        "account_type": "Business",
        "status": "active",
        "phone": "+55 11 99999-9999",
        "devices": ["Maquininha Pro", "App Mobile"],
    },
    "maria@business.com": {
        "name": "Maria Santos",
        "account_type": "Premium",
        "status": "active",
        "phone": "+55 21 88888-8888",
        "devices": ["PDV Terminal", "Tap to Pay"],
    },
}


def create_support_ticket(
    customer_email: str, subject: str, description: str, priority: str = "medium"
) -> Dict[str, Any]:
    """
    Create a new support ticket for a customer issue.

    Args:
        customer_email: Customer's email address (required)
        subject: Brief description of the issue (required)
        description: Detailed description of the problem (required)
        priority: Priority level - must be one of: low, medium, high, urgent (default: medium)

    Returns:
        Dict[str, Any]: Dictionary containing:
            - success (bool): Whether the ticket was created successfully
            - message (str): Success or error message
            - ticket_id (str): Generated ticket ID (if successful)
            - status (str): Ticket status (if successful)
            - priority (str): Ticket priority (if successful)

    Raises:
        ValueError: If required parameters are missing or invalid
    """
    global TICKET_COUNTER

    try:
        # Input validation
        if not customer_email or not customer_email.strip():
            raise ValueError("Customer email is required")
        if not subject or not subject.strip():
            raise ValueError("Subject is required")
        if not description or not description.strip():
            raise ValueError("Description is required")

        # Normalize inputs
        customer_email = customer_email.lower().strip()
        subject = subject.strip()
        description = description.strip()

        # Validate priority
        valid_priorities = ["low", "medium", "high", "urgent"]
        if priority.lower() not in valid_priorities:
            logger.warning(f"Invalid priority '{priority}', defaulting to 'medium'")
            priority = "medium"

        # Generate unique ticket ID
        ticket_id = f"TK-{TICKET_COUNTER}"
        TICKET_COUNTER += 1

        # Create ticket record
        ticket = {
            "ticket_id": ticket_id,
            "customer_email": customer_email,
            "subject": subject,
            "description": description,
            "priority": priority.lower(),
            "status": "open",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "assigned_to": "support_team",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Store ticket
        TICKETS[ticket_id] = ticket

        logger.info(f"Created support ticket {ticket_id} for {customer_email}")

        return {
            "success": True,
            "message": f"Support ticket {ticket_id} has been created successfully!",
            "ticket_id": ticket_id,
            "status": "open",
            "priority": priority.lower(),
        }

    except ValueError as e:
        logger.error(f"Validation error creating ticket: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to create ticket: {str(e)}",
        }
    except Exception as e:
        logger.error(f"Unexpected error creating ticket: {str(e)}")
        return {
            "success": False,
            "message": "An unexpected error occurred while creating the ticket",
        }


def lookup_customer_info(email: str) -> Dict[str, Any]:
    """
    Look up customer information by email address.

    Args:
        email: Customer's email address to search for

    Returns:
        Dict[str, Any]: Dictionary containing:
            - success (bool): Whether the lookup was successful
            - customer_found (bool): Whether a customer was found
            - message (str): Status message
            - Additional customer fields if found (name, account_type, etc.)

    Raises:
        ValueError: If email parameter is invalid
    """
    try:
        # Input validation
        if not email or not email.strip():
            raise ValueError("Email address is required")

        # Normalize email
        email = email.lower().strip()

        # Basic email format validation
        if "@" not in email or "." not in email:
            logger.warning(f"Invalid email format: {email}")
            return {
                "success": False,
                "customer_found": False,
                "message": f"Invalid email format: {email}",
            }

        # Look up customer
        if email in CUSTOMERS:
            customer = CUSTOMERS[email]
            logger.info(f"Found customer: {customer['name']} ({email})")

            return {
                "success": True,
                "customer_found": True,
                "name": customer["name"],
                "account_type": customer["account_type"],
                "status": customer["status"],
                "phone": customer["phone"],
                "devices": customer["devices"],
                "message": f"Found customer: {customer['name']}",
            }
        else:
            logger.info(f"No customer found with email: {email}")
            return {
                "success": True,
                "customer_found": False,
                "message": f"No customer found with email: {email}",
            }

    except ValueError as e:
        logger.error(f"Validation error in customer lookup: {str(e)}")
        return {
            "success": False,
            "customer_found": False,
            "message": str(e),
        }
    except Exception as e:
        logger.error(f"Unexpected error in customer lookup: {str(e)}")
        return {
            "success": False,
            "customer_found": False,
            "message": "An unexpected error occurred during customer lookup",
        }


def check_ticket_status(ticket_id: str) -> Dict[str, Any]:
    """
    Check the status of an existing support ticket.

    Args:
        ticket_id: The ticket ID to look up (e.g., TK-1000)

    Returns:
        Dict[str, Any]: Dictionary containing:
            - success (bool): Whether the lookup was successful
            - ticket_found (bool): Whether the ticket was found
            - message (str): Status message
            - Additional ticket fields if found (status, priority, etc.)

    Raises:
        ValueError: If ticket_id parameter is invalid
    """
    try:
        # Input validation
        if not ticket_id or not ticket_id.strip():
            raise ValueError("Ticket ID is required")

        ticket_id = ticket_id.strip().upper()

        # Look up ticket
        if ticket_id in TICKETS:
            ticket = TICKETS[ticket_id]
            logger.info(f"Found ticket {ticket_id} with status: {ticket['status']}")

            return {
                "success": True,
                "ticket_found": True,
                "ticket_id": ticket["ticket_id"],
                "status": ticket["status"],
                "priority": ticket["priority"],
                "subject": ticket["subject"],
                "created_at": ticket["created_at"],
                "assigned_to": ticket["assigned_to"],
                "updated_at": ticket.get("updated_at", ticket["created_at"]),
                "message": f"Ticket {ticket_id} status: {ticket['status']}",
            }
        else:
            logger.info(f"Ticket not found: {ticket_id}")
            return {
                "success": True,
                "ticket_found": False,
                "message": f"Ticket {ticket_id} not found in the system",
            }

    except ValueError as e:
        logger.error(f"Validation error in ticket lookup: {str(e)}")
        return {
            "success": False,
            "ticket_found": False,
            "message": str(e),
        }
    except Exception as e:
        logger.error(f"Unexpected error in ticket lookup: {str(e)}")
        return {
            "success": False,
            "ticket_found": False,
            "message": "An unexpected error occurred during ticket lookup",
        }


def get_customer_support_agent() -> Agent:
    """
    Create and configure the customer support agent.

    Returns:
        Agent: Configured customer support agent instance

    Raises:
        ValueError: If required configuration is missing
    """
    if not API_KEY:
        raise ValueError("MISTRAL_API_KEY is required")

    try:
        agent = Agent(
            name="Customer Support Agent",
            model=MistralChat(api_key=API_KEY, id=LLM_MODEL),
            debug_mode=True,
            show_tool_calls=True,
            tools=[create_support_ticket, lookup_customer_info, check_ticket_status],
            instructions=customer_support_agent_instructions,
            response_model=AgentResponseOutput,
        )
        logger.info("Customer support agent initialized successfully")
        return agent
    except Exception as e:
        logger.error(f"Failed to initialize customer support agent: {str(e)}")
        raise


# Create the customer support agent instance
customer_support_agent = get_customer_support_agent()
