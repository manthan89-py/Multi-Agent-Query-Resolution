import pytest
from unittest.mock import patch, Mock
import os

from agents.workflow import IntelligentQueryResolver
from agents.router_agent import create_customer_support_team
from agno.storage.json import JsonStorage


class TestIntegration:
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.router_agent_team')
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    @patch('agents.router_agent.Team')
    @patch('agents.router_agent.MistralChat')
    def test_workflow_router_integration(self, router_mistral, router_team, 
                                        workflow_mistral, workflow_agent, workflow_router):
        """Test integration between workflow and router components"""
        # Setup router team
        mock_router_team_instance = Mock()
        router_team.return_value = mock_router_team_instance
        
        # Setup workflow
        mock_workflow_agent = Mock()
        mock_personality_response = Mock()
        mock_personality_response.content = Mock()
        mock_personality_response.content.response = 'Enhanced response'
        mock_workflow_agent.run.return_value = mock_personality_response
        workflow_agent.return_value = mock_workflow_agent
        
        # Setup team response
        mock_team_response = Mock()
        mock_team_response.content = Mock()
        mock_team_response.content.model_dump.return_value = {
            'response': 'Router response',
            'agent_workflow': {'agent_name': 'TestAgent'}
        }
        workflow_router.run.return_value = mock_team_response
        
        # Test integration
        workflow = IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
        result = workflow.run("Test integration query")
        
        assert result.event.name == "workflow_completed"
        workflow_router.run.assert_called_once_with("Test integration query")
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.router_agent.Team')
    @patch('agents.router_agent.MistralChat')
    def test_router_team_creation_in_workflow_context(self, mock_mistral, mock_team):
        """Test router team creation works in workflow context"""
        mock_team_instance = Mock()
        mock_team.return_value = mock_team_instance
        
        team = create_customer_support_team()
        
        assert team == mock_team_instance
        mock_team.assert_called_once()
        
        # Verify team configuration is suitable for workflow
        call_args = mock_team.call_args
        assert call_args[1]['mode'] == "route"  # Required for workflow routing
        assert call_args[1]['response_model'] is not None  # Required for structured responses


class TestErrorHandling:
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.router_agent_team')
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    def test_workflow_handles_router_exceptions(self, mock_mistral, mock_agent, mock_router):
        """Test that workflow properly handles router exceptions"""
        mock_router.run.side_effect = Exception("Router failed")
        
        workflow = IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
        result = workflow.run("Test query")
        
        assert result.event.name == "workflow_failed"
        assert "Unexpected error" in result.messages[0]
    
    @patch.dict('os.environ', {}, clear=True)
    def test_missing_api_key_in_both_modules(self):
        """Test that both modules handle missing API key"""
        with pytest.raises(ValueError, match="MISTRAL_API_KEY environment variable is required"):
            # Test router module
            import importlib
            import agents.router_agent
            importlib.reload(agents.router_agent)
        
        with pytest.raises(ValueError, match="MISTRAL_API_KEY environment variable is required"):
            # Test workflow module
            IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
