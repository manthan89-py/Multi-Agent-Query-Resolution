# tests/conftest.py

import pytest
from unittest.mock import Mock


@pytest.fixture
def mock_mistral_chat():
    """Fixture for MistralChat mock"""
    return Mock()


@pytest.fixture
def mock_agent():
    """Fixture for Agent mock"""
    return Mock()


@pytest.fixture
def mock_team():
    """Fixture for Team mock"""
    return Mock()


@pytest.fixture
def mock_storage():
    """Fixture for JsonStorage mock"""
    return Mock()


@pytest.fixture
def sample_query():
    """Fixture for sample query"""
    return "What is your return policy?"


@pytest.fixture
def sample_team_response():
    """Fixture for sample team response"""
    mock_response = Mock()
    mock_response.content = Mock()
    mock_response.content.model_dump.return_value = {
        'response': 'Original response from team',
        'agent_workflow': {'agent_name': 'CustomerSupportAgent'},
        'confidence': 0.9
    }
    return mock_response


@pytest.fixture
def sample_personality_response():
    """Fixture for sample personality response"""
    mock_response = Mock()
    mock_response.content = Mock()
    mock_response.content.response = 'Enhanced response with personality'
    return mock_response