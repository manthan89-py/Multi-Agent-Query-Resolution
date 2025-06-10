# tests/test_router_agent.py

import pytest
from unittest.mock import patch, Mock
import os

from agents.router_agent import create_customer_support_team


class TestCreateCustomerSupportTeam:
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.router_agent.Team')
    @patch('agents.router_agent.MistralChat')
    @patch('agents.router_agent.customer_support_agent')
    @patch('agents.router_agent.knowledge_agent')
    def test_create_customer_support_team_success(self, mock_knowledge_agent, 
                                                 mock_customer_support_agent, 
                                                 mock_mistral_chat, mock_team):
        """Test successful team creation"""
        mock_team_instance = Mock()
        mock_team.return_value = mock_team_instance
        mock_mistral_instance = Mock()
        mock_mistral_chat.return_value = mock_mistral_instance
        
        result = create_customer_support_team()
        
        assert result == mock_team_instance
        mock_mistral_chat.assert_called_once_with(
            api_key='test-api-key', 
            id='mistral-large-latest'
        )
        mock_team.assert_called_once()
        
        # Verify team configuration
        call_args = mock_team.call_args
        assert call_args[1]['name'] == "Customer Support and Product Inquiry Team"
        assert call_args[1]['mode'] == "route"
        assert call_args[1]['model'] == mock_mistral_instance
        assert mock_customer_support_agent in call_args[1]['members']
        assert mock_knowledge_agent in call_args[1]['members']
        assert call_args[1]['markdown'] is True
        assert call_args[1]['show_members_responses'] is True
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.router_agent.Team', side_effect=Exception("Team creation failed"))
    def test_create_customer_support_team_failure(self, mock_team):
        """Test team creation failure"""
        with pytest.raises(Exception, match="Team creation failed"):
            create_customer_support_team()
    
    @patch.dict('os.environ', {}, clear=True)
    def test_create_customer_support_team_missing_api_key(self):
        """Test team creation without API key"""
        with pytest.raises(ValueError, match="MISTRAL_API_KEY environment variable is required"):
            # This would happen during module import
            import importlib
            import agents.router_agent
            importlib.reload(agents.router_agent)


class TestEnvironmentConfiguration:
    
    def test_api_key_validation(self):
        """Test API key validation"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError):
                # API key should be required
                exec("API_KEY = os.getenv('MISTRAL_API_KEY')\nif not API_KEY:\n    raise ValueError('MISTRAL_API_KEY environment variable is required')")
    
    def test_llm_model_default(self):
        """Test LLM model default value"""
        with patch.dict('os.environ', {}, clear=True):
            llm_model = os.getenv("LLM_MODEL", "mistral-large-latest")
            assert llm_model == "mistral-large-latest"
    
    def test_llm_model_custom(self):
        """Test custom LLM model"""
        with patch.dict('os.environ', {'LLM_MODEL': 'custom-model'}):
            llm_model = os.getenv("LLM_MODEL", "mistral-large-latest")
            assert llm_model == "custom-model"


class TestTeamConfiguration:
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.router_agent.Team')
    @patch('agents.router_agent.MistralChat')
    def test_team_routing_mode(self, mock_mistral_chat, mock_team):
        """Test that team is configured in routing mode"""
        mock_team_instance = Mock()
        mock_team.return_value = mock_team_instance
        
        create_customer_support_team()
        
        call_args = mock_team.call_args
        assert call_args[1]['mode'] == "route"
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.router_agent.Team')
    @patch('agents.router_agent.MistralChat')
    def test_team_markdown_enabled(self, mock_mistral_chat, mock_team):
        """Test that team has markdown enabled"""
        mock_team_instance = Mock()
        mock_team.return_value = mock_team_instance
        
        create_customer_support_team()
        
        call_args = mock_team.call_args
        assert call_args[1]['markdown'] is True
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.router_agent.Team')
    @patch('agents.router_agent.MistralChat')
    def test_team_show_members_responses(self, mock_mistral_chat, mock_team):
        """Test that team shows member responses"""
        mock_team_instance = Mock()
        mock_team.return_value = mock_team_instance
        
        create_customer_support_team()
        
        call_args = mock_team.call_args
        assert call_args[1]['show_members_responses'] is True


class TestAgentMembers:
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.router_agent.Team')
    @patch('agents.router_agent.MistralChat')
    @patch('agents.router_agent.customer_support_agent')
    @patch('agents.router_agent.knowledge_agent')
    def test_team_has_correct_members(self, mock_knowledge_agent, 
                                     mock_customer_support_agent, 
                                     mock_mistral_chat, mock_team):
        """Test that team has both required agent members"""
        mock_team_instance = Mock()
        mock_team.return_value = mock_team_instance
        
        create_customer_support_team()
        
        call_args = mock_team.call_args
        members = call_args[1]['members']
        
        assert len(members) == 2
        assert mock_customer_support_agent in members
        assert mock_knowledge_agent in members
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.router_agent.Team')
    @patch('agents.router_agent.MistralChat')
    @patch('agents.router_agent.customer_support_agent', None)
    @patch('agents.router_agent.knowledge_agent')
    def test_team_with_missing_customer_support_agent(self, mock_knowledge_agent, 
                                                     mock_mistral_chat, mock_team):
        """Test team creation with missing customer support agent"""
        mock_team_instance = Mock()
        mock_team.return_value = mock_team_instance
        
        create_customer_support_team()
        
        call_args = mock_team.call_args
        members = call_args[1]['members']
        
        # Should still include the None agent (will be handled by Team class)
        assert None in members
        assert mock_knowledge_agent in members


class TestResponseModel:
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.router_agent.Team')
    @patch('agents.router_agent.MistralChat')
    @patch('agents.router_agent.AgentResponseOutput')
    def test_team_response_model(self, mock_response_output, mock_mistral_chat, mock_team):
        """Test that team uses correct response model"""
        mock_team_instance = Mock()
        mock_team.return_value = mock_team_instance
        
        create_customer_support_team()
        
        call_args = mock_team.call_args
        assert call_args[1]['response_model'] == mock_response_output


class TestInstructions:
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.router_agent.Team')
    @patch('agents.router_agent.MistralChat')
    @patch('agents.router_agent.router_agent_instructions')
    def test_team_instructions(self, mock_instructions, mock_mistral_chat, mock_team):
        """Test that team uses router agent instructions"""
        mock_team_instance = Mock()
        mock_team.return_value = mock_team_instance
        
        create_customer_support_team()
        
        call_args = mock_team.call_args
        assert call_args[1]['instructions'] == mock_instructions


class TestModuleInitialization:
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.router_agent.create_customer_support_team')
    def test_module_initialization(self, mock_create_team):
        """Test that module initializes correctly"""
        from agents import router_agent

        assert router_agent.create_customer_support_team == mock_create_team