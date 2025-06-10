# tests/test_customer_support_agent.py

import pytest
from unittest.mock import patch, Mock
from datetime import datetime

from agents.customer_support_agent import (
    create_support_ticket,
    lookup_customer_info,
    check_ticket_status,
    get_customer_support_agent,
    TICKETS,
    CUSTOMERS,
    TICKET_COUNTER
)


class TestCreateSupportTicket:
    
    def setup_method(self):
        """Clear tickets before each test"""
        global TICKETS, TICKET_COUNTER
        TICKETS.clear()
        TICKET_COUNTER = 1000
    
    def test_create_support_ticket_success(self):
        """Test successful ticket creation"""
        result = create_support_ticket(
            customer_email="test@example.com",
            subject="Test Issue",
            description="Test description",
            priority="high"
        )
        
        assert result["success"] is True
        assert "TK-1000" in result["message"]
        assert result["ticket_id"] == "TK-1000"
        assert result["status"] == "open"
        assert result["priority"] == "high"
        assert "TK-1000" in TICKETS
    
    def test_create_support_ticket_missing_email(self):
        """Test ticket creation with missing email"""
        result = create_support_ticket(
            customer_email="",
            subject="Test Issue",
            description="Test description"
        )
        
        assert result["success"] is False
        assert "Customer email is required" in result["message"]
    
    def test_create_support_ticket_missing_subject(self):
        """Test ticket creation with missing subject"""
        result = create_support_ticket(
            customer_email="test@example.com",
            subject="",
            description="Test description"
        )
        
        assert result["success"] is False
        assert "Subject is required" in result["message"]
    
    def test_create_support_ticket_missing_description(self):
        """Test ticket creation with missing description"""
        result = create_support_ticket(
            customer_email="test@example.com",
            subject="Test Issue",
            description=""
        )
        
        assert result["success"] is False
        assert "Description is required" in result["message"]
    
    def test_create_support_ticket_invalid_priority(self):
        """Test ticket creation with invalid priority defaults to medium"""
        result = create_support_ticket(
            customer_email="test@example.com",
            subject="Test Issue",
            description="Test description",
            priority="invalid"
        )
        
        assert result["success"] is True
        assert result["priority"] == "medium"
    
    def test_create_support_ticket_increments_counter(self):
        """Test that ticket counter increments correctly"""
        result1 = create_support_ticket(
            customer_email="test1@example.com",
            subject="Issue 1",
            description="Description 1"
        )
        
        result2 = create_support_ticket(
            customer_email="test2@example.com",
            subject="Issue 2",
            description="Description 2"
        )
        
        assert result1["ticket_id"] == "TK-1000"
        assert result2["ticket_id"] == "TK-1001"


class TestLookupCustomerInfo:
    
    def test_lookup_existing_customer(self):
        """Test looking up an existing customer"""
        result = lookup_customer_info("john@example.com")
        
        assert result["success"] is True
        assert result["customer_found"] is True
        assert result["name"] == "John Silva"
        assert result["account_type"] == "Business"
        assert result["status"] == "active"
        assert result["phone"] == "+55 11 99999-9999"
        assert "Maquininha Pro" in result["devices"]
    
    def test_lookup_nonexistent_customer(self):
        """Test looking up a non-existent customer"""
        result = lookup_customer_info("nonexistent@example.com")
        
        assert result["success"] is True
        assert result["customer_found"] is False
        assert "No customer found" in result["message"]
    
    def test_lookup_customer_empty_email(self):
        """Test lookup with empty email"""
        result = lookup_customer_info("")
        
        assert result["success"] is False
        assert result["customer_found"] is False
        assert "Email address is required" in result["message"]
    
    def test_lookup_customer_invalid_email_format(self):
        """Test lookup with invalid email format"""
        result = lookup_customer_info("invalid-email")
        
        assert result["success"] is False
        assert result["customer_found"] is False
        assert "Invalid email format" in result["message"]
    
    def test_lookup_customer_case_insensitive(self):
        """Test that email lookup is case insensitive"""
        result = lookup_customer_info("JOHN@EXAMPLE.COM")
        
        assert result["success"] is True
        assert result["customer_found"] is True
        assert result["name"] == "John Silva"


class TestCheckTicketStatus:
    
    def setup_method(self):
        """Setup test tickets"""
        global TICKETS
        TICKETS.clear()
        TICKETS["TK-1000"] = {
            "ticket_id": "TK-1000",
            "customer_email": "test@example.com",
            "subject": "Test Issue",
            "description": "Test description",
            "priority": "medium",
            "status": "open",
            "created_at": "2024-01-01 10:00:00",
            "assigned_to": "support_team",
            "updated_at": "2024-01-01 10:00:00"
        }
    
    def test_check_existing_ticket_status(self):
        """Test checking status of existing ticket"""
        result = check_ticket_status("TK-1000")
        
        assert result["success"] is True
        assert result["ticket_found"] is True
        assert result["ticket_id"] == "TK-1000"
        assert result["status"] == "open"
        assert result["priority"] == "medium"
        assert result["subject"] == "Test Issue"
        assert result["created_at"] == "2024-01-01 10:00:00"
    
    def test_check_nonexistent_ticket_status(self):
        """Test checking status of non-existent ticket"""
        result = check_ticket_status("TK-9999")
        
        assert result["success"] is True
        assert result["ticket_found"] is False
        assert "not found" in result["message"]
    
    def test_check_ticket_status_empty_id(self):
        """Test checking status with empty ticket ID"""
        result = check_ticket_status("")
        
        assert result["success"] is False
        assert result["ticket_found"] is False
        assert "Ticket ID is required" in result["message"]
    
    def test_check_ticket_status_case_handling(self):
        """Test that ticket ID is handled case-insensitively"""
        result = check_ticket_status("tk-1000")
        
        assert result["success"] is True
        assert result["ticket_found"] is True
        assert result["ticket_id"] == "TK-1000"


class TestGetCustomerSupportAgent:
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    def test_get_customer_support_agent_success(self):
        """Test successful agent creation"""
        with patch('agents.customer_support_agent.Agent') as mock_agent:
            mock_agent.return_value = Mock()
            agent = get_customer_support_agent()
            
            assert agent is not None
            mock_agent.assert_called_once()
    
    @patch.dict('os.environ', {}, clear=True)
    def test_get_customer_support_agent_missing_api_key(self):
        """Test agent creation without API key"""
        with pytest.raises(ValueError, match="MISTRAL_API_KEY is required"):
            get_customer_support_agent()
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    def test_get_customer_support_agent_initialization_error(self):
        """Test agent creation with initialization error"""
        with patch('agents.customer_support_agent.Agent', side_effect=Exception("Init error")):
            with pytest.raises(Exception, match="Init error"):
                get_customer_support_agent()


class TestIntegration:
    
    def setup_method(self):
        """Setup for integration tests"""
        global TICKETS, TICKET_COUNTER
        TICKETS.clear()
        TICKET_COUNTER = 1000
    
    def test_full_support_workflow(self):
        """Test complete support workflow"""
        # Create a ticket
        ticket_result = create_support_ticket(
            customer_email="john@example.com",
            subject="Payment Issue",
            description="Unable to process payment",
            priority="high"
        )
        
        assert ticket_result["success"] is True
        ticket_id = ticket_result["ticket_id"]
        
        # Look up customer info
        customer_result = lookup_customer_info("john@example.com")
        assert customer_result["success"] is True
        assert customer_result["customer_found"] is True
        
        # Check ticket status
        status_result = check_ticket_status(ticket_id)
        assert status_result["success"] is True
        assert status_result["ticket_found"] is True
        assert status_result["status"] == "open"