import pytest
from unittest.mock import Mock, patch
import os
from pathlib import Path

@pytest.fixture
def mock_openai():
    """Mock OpenAI API calls"""
    with patch('langchain_openai.ChatOpenAI') as mock:
        yield mock

@pytest.fixture
def sample_knowledge_base():
    """Sample knowledge base data"""
    return {
        "policy_types": {
            "term_life": {
                "description": "Test term life policy",
                "benefits": ["Test benefit"],
                "eligibility": "Test eligibility",
                "duration": "Test duration"
            }
        },
        "common_questions": {
            "eligibility": {"test": "test"},
            "claims_process": {"test": "test"}
        }
    }

@pytest.fixture
def temp_knowledge_file(tmp_path, sample_knowledge_base):
    """Create temporary knowledge file"""
    file_path = tmp_path / "insurance_data.json"
    file_path.write_text(json.dumps(sample_knowledge_base))
    return file_path