# tests/test_workflow.py

import pytest
from unittest.mock import patch, Mock, MagicMock
import os
from textwrap import dedent

from agno.workflow import RunEvent, RunResponse
from agno.storage.json import JsonStorage

from agents.workflow import IntelligentQueryResolver
from utils import PersonalityLayerResponse, FinalResponseOutput
from agno.storage.json import JsonStorage


class TestIntelligentQueryResolverInit:
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    def test_init_success(self, mock_mistral_chat, mock_agent):
        """Test successful workflow initialization"""
        mock_agent_instance = Mock()
        mock_agent.return_value = mock_agent_instance
        mock_mistral_instance = Mock()
        mock_mistral_chat.return_value = mock_mistral_instance
        
        workflow = IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
        
        assert hasattr(workflow, 'personality_layer')
        assert workflow.personality_layer == mock_agent_instance
        mock_mistral_chat.assert_called_once_with(
            api_key='test-api-key', 
            id='mistral-large-latest'
        )
        mock_agent.assert_called_once()
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    def test_init_with_storage(self, mock_mistral_chat, mock_agent):
        """Test workflow initialization with storage"""
        mock_storage = Mock(spec=JsonStorage)
        workflow = IntelligentQueryResolver(storage=mock_storage)
        
        assert hasattr(workflow, 'personality_layer')
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.Agent', side_effect=Exception("Agent creation failed"))
    def test_init_personality_layer_failure(self, mock_agent):
        """Test workflow initialization failure during personality layer setup"""
        with pytest.raises(Exception, match="Agent creation failed"):
            IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
    
    @patch.dict('os.environ', {}, clear=True)
    def test_init_missing_api_key(self):
        """Test workflow initialization without API key"""
        with pytest.raises(ValueError, match="MISTRAL_API_KEY environment variable is required"):
            IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))


class TestIntelligentQueryResolverRun:
    
    def setup_method(self):
        """Setup method for each test"""
        self.mock_team_response = Mock()
        self.mock_team_response.content = Mock()
        self.mock_team_response.content.model_dump.return_value = {
            'response': 'Original response',
            'agent_workflow': {'agent_name': 'TestAgent'}
        }
        
        self.mock_personality_response = Mock()
        self.mock_personality_response.content = Mock()
        self.mock_personality_response.content.response = 'Enhanced response'
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.router_agent_team')
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    @patch('agents.workflow.FinalResponseOutput')
    def test_run_success(self, mock_final_response, mock_mistral_chat, 
                        mock_agent, mock_router_team):
        """Test successful workflow execution"""
        # Setup mocks
        mock_agent_instance = Mock()
        mock_agent_instance.run.return_value = self.mock_personality_response
        mock_agent.return_value = mock_agent_instance
        mock_router_team.run.return_value = self.mock_team_response
        mock_final_instance = Mock()
        mock_final_response.return_value = mock_final_instance
        
        workflow = IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
        result = workflow.run(query="Test query")
        
        # Assertions
        assert isinstance(result, RunResponse)
        assert result.content == mock_final_instance
        assert result.event == RunEvent.workflow_completed
        mock_router_team.run.assert_called_once_with("Test query")
        mock_agent_instance.run.assert_called_once_with("Original response")
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    def test_run_empty_query(self, mock_mistral_chat, mock_agent):
        """Test workflow execution with empty query"""
        workflow = IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
        result = workflow.run(query="")
        
        assert result.content is None
        assert result.event == RunEvent.workflow_failed
        assert "Validation error" in result.messages[0]
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    def test_run_whitespace_query(self, mock_mistral_chat, mock_agent):
        """Test workflow execution with whitespace-only query"""
        workflow = IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
        result = workflow.run(query="   ")
        
        assert result.content is None
        assert result.event == RunEvent.workflow_failed
        assert "Validation error" in result.messages[0]
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.router_agent_team')
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    def test_run_router_team_failure(self, mock_mistral_chat, mock_agent, mock_router_team):
        """Test workflow execution when router team fails"""
        mock_router_team.run.return_value = None
        
        workflow = IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
        result = workflow.run(query="Test query")
        
        assert result.content is None
        assert result.event == RunEvent.workflow_failed
        assert "Workflow error" in result.messages[0]
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.router_agent_team')
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    def test_run_empty_team_response(self, mock_mistral_chat, mock_agent, mock_router_team):
        """Test workflow execution when team response is empty"""
        mock_team_response = Mock()
        mock_team_response.content = None
        mock_router_team.run.return_value = mock_team_response
        
        workflow = IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
        result = workflow.run(query="Test query")
        
        assert result.content is None
        assert result.event == RunEvent.workflow_failed
        assert "Workflow error" in result.messages[0]
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.router_agent_team')
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    def test_run_personality_layer_failure(self, mock_mistral_chat, mock_agent, mock_router_team):
        """Test workflow execution when personality layer fails"""
        mock_agent_instance = Mock()
        mock_agent_instance.run.return_value = None
        mock_agent.return_value = mock_agent_instance
        mock_router_team.run.return_value = self.mock_team_response
        
        workflow = IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
        result = workflow.run(query="Test query")
        
        assert result.content is None
        assert result.event == RunEvent.workflow_failed
        assert "Workflow error" in result.messages[0]
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.router_agent_team')
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    def test_run_unexpected_exception(self, mock_mistral_chat, mock_agent, mock_router_team):
        """Test workflow execution with unexpected exception"""
        mock_router_team.run.side_effect = Exception("Unexpected error")
        
        workflow = IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
        result = workflow.run(query="Test query")
        
        assert result.content is None
        assert result.event == RunEvent.workflow_failed
        assert "Unexpected error" in result.messages[0]


class TestIntelligentQueryResolverHealthCheck:
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.router_agent_team')
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    def test_health_check_success(self, mock_mistral_chat, mock_agent, mock_router_team):
        """Test successful health check"""
        workflow = IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
        result = workflow.health_check()
        
        assert result is True
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.router_agent_team', None)
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    def test_health_check_router_team_unavailable(self, mock_mistral_chat, mock_agent):
        """Test health check when router team is unavailable"""
        workflow = IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
        result = workflow.health_check()
        
        assert result is False
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    def test_health_check_personality_layer_missing(self, mock_mistral_chat, mock_agent):
        """Test health check when personality layer is missing"""
        workflow = IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
        workflow.personality_layer = None
        result = workflow.health_check()
        
        assert result is False
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.router_agent_team')
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    def test_health_check_exception(self, mock_mistral_chat, mock_agent, mock_router_team):
        """Test health check with exception"""
        workflow = IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
        # Force an exception by deleting the personality_layer attribute
        delattr(workflow, 'personality_layer')
        
        result = workflow.health_check()
        
        assert result is False


class TestWorkflowConfiguration:
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    def test_workflow_description(self, mock_mistral_chat, mock_agent):
        """Test workflow description is set correctly"""
        workflow = IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
        
        assert workflow.description is not None
        assert "This workflow resolves customer queries" in workflow.description
        assert "Query routing to specialized agents" in workflow.description
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key', 'LLM_MODEL': 'custom-model'})
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    def test_custom_llm_model(self, mock_mistral_chat, mock_agent):
        """Test workflow with custom LLM model"""
        workflow = IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
        
        mock_mistral_chat.assert_called_once_with(
            api_key='test-api-key',
            id='custom-model'
        )
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    def test_personality_layer_configuration(self, mock_mistral_chat, mock_agent):
        """Test personality layer configuration"""
        workflow = IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
        
        call_args = mock_agent.call_args
        assert call_args[1]['name'] == "Personality AI"
        assert call_args[1]['description'] == "AI agent that adds conversational personality and warmth to responses"
        assert call_args[1]['tools'] == []
        assert call_args[1]['response_model'] == PersonalityLayerResponse
        assert call_args[1]['debug_mode'] is True


class TestResponseProcessing:
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.router_agent_team')
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    @patch('agents.workflow.FinalResponseOutput')
    def test_response_swapping(self, mock_final_response, mock_mistral_chat, 
                              mock_agent, mock_router_team):
        """Test that original and enhanced responses are properly swapped"""
        # Setup mocks
        mock_agent_instance = Mock()
        mock_personality_response = Mock()
        mock_personality_response.content = Mock()
        mock_personality_response.content.response = 'Enhanced response'
        mock_agent_instance.run.return_value = mock_personality_response
        mock_agent.return_value = mock_agent_instance
        
        mock_team_response = Mock()
        mock_team_response.content = Mock()
        mock_team_response.content.model_dump.return_value = {
            'response': 'Original response',
            'agent_workflow': {'agent_name': 'TestAgent'}
        }
        mock_router_team.run.return_value = mock_team_response
        
        workflow = IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
        workflow.run(query="Test query")
        
        # Verify that FinalResponseOutput was called with swapped responses
        call_args = mock_final_response.call_args[1]
        assert call_args['response'] == 'Enhanced response'
        assert call_args['source_agent_response'] == 'Original response'
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.workflow.router_agent_team')
    @patch('agents.workflow.Agent')
    @patch('agents.workflow.MistralChat')
    def test_empty_original_response(self, mock_mistral_chat, mock_agent, mock_router_team):
        """Test handling of empty original response"""
        mock_team_response = Mock()
        mock_team_response.content = Mock()
        mock_team_response.content.model_dump.return_value = {
            'response': '',
            'agent_workflow': {'agent_name': 'TestAgent'}
        }
        mock_router_team.run.return_value = mock_team_response
        
        workflow = IntelligentQueryResolver(storage=JsonStorage("storage/test_workflow.json"))
        result = workflow.run(query="Test query")
        
        assert result.content is None
        assert result.event == RunEvent.workflow_failed
        assert "Workflow error" in result.messages[0]
