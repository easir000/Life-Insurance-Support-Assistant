import pytest
from unittest.mock import Mock, patch
import json
import os
from app.agent import InsuranceAgent
from app.models import MessageRequest

def test_agent_initialization():
    """Test agent initialization"""
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
        agent = InsuranceAgent()
        assert agent is not None
        assert hasattr(agent, 'llm')
        assert hasattr(agent, 'sessions')
        assert hasattr(agent, 'knowledge_base')

def test_process_message_basic():
    """Test basic message processing"""
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
        agent = InsuranceAgent()
        response = agent.process_message(
            user_id="test_user",
            message="Hello"
        )
        
        assert response.response is not None
        assert len(response.response) > 0
        assert response.session_id is not None

def test_session_management():
    """Test session creation and management"""
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
        agent = InsuranceAgent()
        
        # First message creates session
        response1 = agent.process_message(
            user_id="test_user",
            message="What is life insurance?"
        )
        
        session_id = response1.session_id
        
        # Second message uses same session
        response2 = agent.process_message(
            user_id="test_user",
            message="Tell me more",
            session_id=session_id
        )
        
        assert response2.session_id == session_id
        assert len(agent.sessions) == 1

def test_query_classification():
    """Test query classification"""
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
        agent = InsuranceAgent()
        assert agent._classify_query("What is term life?") == "policy_type"
        assert agent._classify_query("Am I eligible?") == "eligibility"
        assert agent._classify_query("How do I file a claim?") == "claims"
        assert agent._classify_query("What does it cover?") == "benefits"
        assert agent._classify_query("How much does it cost?") == "cost"

def test_empty_message_handling():
    """Test handling of empty messages"""
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
        agent = InsuranceAgent()
        with pytest.raises(ValueError):
            agent.process_message(user_id="test_user", message="")