# custtomer_support_agent.py

import os
import asyncio
from agno.agent import Agent
from agno.models.mistral import MistralChat
from dotenv import load_dotenv
from typing import Dict, Any
from datetime import datetime
from instructions import customer_support_agent_instructions
from models import AgentResponseOutput

load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")

if not API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable is required")

# In-memory storage for demo purposes
TICKETS = {}
TICKET_COUNTER = 1000

# Mock customer database
CUSTOMERS = {
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
    """Create a new support ticket for a customer issue

    Args:
        customer_email: Customer's email address
        subject: Brief description of the issue
        description: Detailed description of the problem
        priority: Priority level (low, medium, high, urgent)

    Returns:
        Dictionary with ticket creation result
    """
    global TICKET_COUNTER

    # Validate priority
    valid_priorities = ["low", "medium", "high", "urgent"]
    if priority.lower() not in valid_priorities:
        priority = "medium"

    # Generate ticket ID
    ticket_id = f"TK-{TICKET_COUNTER}"
    TICKET_COUNTER += 1

    # Create ticket
    ticket = {
        "ticket_id": ticket_id,
        "customer_email": customer_email.lower().strip(),
        "subject": subject,
        "description": description,
        "priority": priority.lower(),
        "status": "open",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "assigned_to": "support_team",
    }

    TICKETS[ticket_id] = ticket

    return {
        "success": True,
        "message": f"Support ticket {ticket_id} has been created successfully!",
        "ticket_id": ticket_id,
        "status": "open",
        "priority": priority.lower(),
    }


def lookup_customer_info(email: str) -> Dict[str, Any]:
    """Look up customer information by email address

    Args:
        email: Customer's email address

    Returns:
        Dictionary with customer information or error message
    """
    email = email.lower().strip()

    if email in CUSTOMERS:
        customer = CUSTOMERS[email]
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
        return {
            "success": False,
            "customer_found": False,
            "message": f"No customer found with email: {email}",
        }


def check_ticket_status(ticket_id: str) -> Dict[str, Any]:
    """Check the status of an existing support ticket

    Args:
        ticket_id: The ticket ID to look up (e.g., TK-1000)

    Returns:
        Dictionary with ticket status information
    """
    if ticket_id in TICKETS:
        ticket = TICKETS[ticket_id]
        return {
            "success": True,
            "ticket_found": True,
            "ticket_id": ticket["ticket_id"],
            "status": ticket["status"],
            "priority": ticket["priority"],
            "subject": ticket["subject"],
            "created_at": ticket["created_at"],
            "assigned_to": ticket["assigned_to"],
            "message": f"Ticket {ticket_id} status: {ticket['status']}",
        }
    else:
        return {
            "success": False,
            "ticket_found": False,
            "message": f"Ticket {ticket_id} not found in the system",
        }


customer_support_agent = Agent(
    name="Customer Support Agent",
    model=MistralChat(api_key=API_KEY, id=os.getenv("LLM_MODEL")),
    debug_mode=True,
    show_tool_calls=True,
    tools=[create_support_ticket, lookup_customer_info, check_ticket_status],
    instructions=customer_support_agent_instructions,
    response_model=AgentResponseOutput,
)


# async def main():
#     """Main function to run the customer support agent"""

#     # Create customer support agent with simple function tools

#     # Test scenarios
#     test_scenarios = [
#         """Hi, I need help with my maquininha. It's not connecting to the network.
#         My email is john@example.com. Subject: Maquininha not connecting.
#         Description: I've tried restarting the device and updating the firmware, but it still doesn't work. Please help!""",
#         "Can you check the status of ticket TK-1000?",
#         "What devices are registered to maria@business.com?",
#     ]

#     print("Testing Customer Support Agent with Function Tools")
#     print("=" * 60)

#     for i, scenario in enumerate(test_scenarios, 1):
#         print(f"\n--- Test Scenario {i} ---")
#         print(f"Customer: {scenario}")
#         print("\nAgent Response:")

#         try:
#             await customer_support.aprint_response(scenario, markdown=True)
#         except Exception as e:
#             print(f"Error: {e}")

#         print("\n" + "-" * 40)


# if __name__ == "__main__":
#     asyncio.run(main())
