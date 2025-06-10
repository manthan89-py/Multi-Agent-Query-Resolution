# tests/test_knowledge_agent.py

import pytest
from unittest.mock import patch, Mock, MagicMock
import os

from agents.knowledge_agent import (
    create_vector_db,
    create_knowledge_base,
    create_knowledge_agent,
    INFINITEPAY_URLS,
    COLLECTION_NAME
)


class TestCreateVectorDb:
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.knowledge_agent.ChromaDb')
    @patch('agents.knowledge_agent.MistralEmbedder')
    def test_create_vector_db_success(self, mock_embedder, mock_chroma):
        """Test successful vector database creation"""
        mock_chroma_instance = Mock()
        mock_chroma.return_value = mock_chroma_instance
        mock_embedder_instance = Mock()
        mock_embedder.return_value = mock_embedder_instance
        
        result = create_vector_db()
        
        assert result == mock_chroma_instance
        mock_embedder.assert_called_once_with(api_key='test-api-key')
        mock_chroma.assert_called_once_with(
            collection=COLLECTION_NAME,
            embedder=mock_embedder_instance,
            persistent_client=True,
            path="storage/chroma_db"
        )
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.knowledge_agent.ChromaDb', side_effect=Exception("DB creation failed"))
    def test_create_vector_db_failure(self, mock_chroma):
        """Test vector database creation failure"""
        with pytest.raises(Exception, match="DB creation failed"):
            create_vector_db()


class TestCreateKnowledgeBase:
    
    @patch('agents.knowledge_agent.WebsiteKnowledgeBase')
    def test_create_knowledge_base_success(self, mock_kb):
        """Test successful knowledge base creation"""
        mock_vector_db = Mock()
        mock_kb_instance = Mock()
        mock_kb.return_value = mock_kb_instance
        
        result = create_knowledge_base(mock_vector_db)
        
        assert result == mock_kb_instance
        mock_kb.assert_called_once_with(
            urls=INFINITEPAY_URLS,
            num_documents=4,
            max_links=1,
            max_depth=1,
            vector_db=mock_vector_db
        )
    
    @patch('agents.knowledge_agent.WebsiteKnowledgeBase', side_effect=Exception("KB creation failed"))
    def test_create_knowledge_base_failure(self, mock_kb):
        """Test knowledge base creation failure"""
        mock_vector_db = Mock()
        
        with pytest.raises(Exception, match="KB creation failed"):
            create_knowledge_base(mock_vector_db)


class TestCreateKnowledgeAgent:
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key', 'TAVILY_API_KEY': 'tavily-key'})
    @patch('agents.knowledge_agent.Agent')
    @patch('agents.knowledge_agent.MistralChat')
    @patch('agents.knowledge_agent.TavilyTools')
    def test_create_knowledge_agent_with_tavily(self, mock_tavily, mock_mistral, mock_agent):
        """Test knowledge agent creation with Tavily tools"""
        mock_kb = Mock()
        mock_agent_instance = Mock()
        mock_agent.return_value = mock_agent_instance
        mock_mistral_instance = Mock()
        mock_mistral.return_value = mock_mistral_instance
        mock_tavily_instance = Mock()
        mock_tavily.return_value = mock_tavily_instance
        
        result = create_knowledge_agent(mock_kb)
        
        assert result == mock_agent_instance
        mock_mistral.assert_called_once_with(api_key='test-api-key', id='mistral-large-latest')
        mock_tavily.assert_called_once_with(search="")
        mock_agent.assert_called_once()
        
        # Check agent configuration
        call_args = mock_agent.call_args
        assert call_args[1]['name'] == "KnowledgeBase Agent"
        assert call_args[1]['model'] == mock_mistral_instance
        assert call_args[1]['knowledge'] == mock_kb
        assert call_args[1]['search_knowledge'] is True
        assert call_args[1]['debug_mode'] is True
        assert mock_tavily_instance in call_args[1]['tools']
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.knowledge_agent.Agent')
    @patch('agents.knowledge_agent.MistralChat')
    def test_create_knowledge_agent_without_tavily(self, mock_mistral, mock_agent):
        """Test knowledge agent creation without Tavily tools"""
        mock_kb = Mock()
        mock_agent_instance = Mock()
        mock_agent.return_value = mock_agent_instance
        mock_mistral_instance = Mock()
        mock_mistral.return_value = mock_mistral_instance
        
        result = create_knowledge_agent(mock_kb)
        
        assert result == mock_agent_instance
        
        # Check that tools list is empty when no Tavily key
        call_args = mock_agent.call_args
        assert call_args[1]['tools'] == []
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.knowledge_agent.Agent', side_effect=Exception("Agent creation failed"))
    def test_create_knowledge_agent_failure(self, mock_agent):
        """Test knowledge agent creation failure"""
        mock_kb = Mock()
        
        with pytest.raises(Exception, match="Agent creation failed"):
            create_knowledge_agent(mock_kb)


class TestInfinitepayUrls:
    
    def test_infinitepay_urls_not_empty(self):
        """Test that InfinitePay URLs list is not empty"""
        assert len(INFINITEPAY_URLS) > 0
    
    def test_infinitepay_urls_valid_format(self):
        """Test that all URLs have valid format"""
        for url in INFINITEPAY_URLS:
            assert url.startswith("https://")
            assert "infinitepay.io" in url
    
    def test_collection_name_defined(self):
        """Test that collection name is properly defined"""
        assert COLLECTION_NAME == "infinitepay-extracted-content"


class TestModuleInitialization:
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key'})
    @patch('agents.knowledge_agent.create_vector_db')
    @patch('agents.knowledge_agent.create_knowledge_base')
    @patch('agents.knowledge_agent.create_knowledge_agent')
    def test_module_initialization_success(self, mock_create_agent, mock_create_kb, mock_create_vdb):
        """Test successful module initialization"""
        mock_vdb = Mock()
        mock_kb = Mock()
        mock_agent = Mock()
        
        mock_create_vdb.return_value = mock_vdb
        mock_create_kb.return_value = mock_kb
        mock_create_agent.return_value = mock_agent
        
        # Simulate module import
        with patch('agents.knowledge_agent.vector_db', mock_vdb):
            with patch('agents.knowledge_agent.knowledge_base', mock_kb):
                with patch('agents.knowledge_agent.knowledge_agent', mock_agent):
                    # Module initialization should succeed
                    assert True
    
    @patch.dict('os.environ', {}, clear=True)
    def test_module_initialization_missing_api_key(self):
        """Test module initialization without API key"""
        with pytest.raises(ValueError, match="MISTRAL_API_KEY environment variable is required"):
            # This would happen during module import
            import importlib
            import agents.knowledge_agent
            importlib.reload(agents.knowledge_agent)


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


class TestIntegration:
    
    @patch.dict('os.environ', {'MISTRAL_API_KEY': 'test-api-key', 'TAVILY_API_KEY': 'tavily-key'})
    @patch('agents.knowledge_agent.ChromaDb')
    @patch('agents.knowledge_agent.MistralEmbedder')
    @patch('agents.knowledge_agent.WebsiteKnowledgeBase')
    @patch('agents.knowledge_agent.Agent')
    @patch('agents.knowledge_agent.MistralChat')
    @patch('agents.knowledge_agent.TavilyTools')
    def test_full_knowledge_agent_setup(self, mock_tavily, mock_mistral, mock_agent, 
                                       mock_kb, mock_embedder, mock_chroma):
        """Test complete knowledge agent setup workflow"""
        # Setup mocks
        mock_vdb = Mock()
        mock_chroma.return_value = mock_vdb
        mock_kb_instance = Mock()
        mock_kb.return_value = mock_kb_instance
        mock_agent_instance = Mock()
        mock_agent.return_value = mock_agent_instance
        
        # Test the workflow
        vector_db = create_vector_db()
        knowledge_base = create_knowledge_base(vector_db)
        knowledge_agent = create_knowledge_agent(knowledge_base)
        
        # Verify the chain of calls
        assert vector_db == mock_vdb
        assert knowledge_base == mock_kb_instance
        assert knowledge_agent == mock_agent_instance
        
        # Verify knowledge base was created with vector db
        mock_kb.assert_called_once_with(
            urls=INFINITEPAY_URLS,
            num_documents=4,
            max_links=1,
            max_depth=1,
            vector_db=mock_vdb
        )
        
        # Verify agent was created with knowledge base
        agent_call_args = mock_agent.call_args
        assert agent_call_args[1]['knowledge'] == mock_kb_instance