import pytest
from app.tools import PolicyTypeTool, EligibilityTool, ClaimsProcessTool

def test_policy_type_tool():
    """Test policy type tool functionality"""
    tool = PolicyTypeTool()
    result = tool._run(policy_type="term life")
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert "term" in result.lower()

def test_policy_type_tool_invalid():
    """Test policy type tool with invalid input"""
    tool = PolicyTypeTool()
    result = tool._run(policy_type="nonexistent policy")
    
    assert isinstance(result, str)
    assert "available" in result.lower()

def test_eligibility_tool():
    """Test eligibility tool functionality"""
    tool = EligibilityTool()
    result = tool._run(age=45, health_status="good")
    
    assert isinstance(result, str)
    assert "45" in result
    assert "good" in result

def test_claims_process_tool():
    """Test claims process tool"""
    tool = ClaimsProcessTool()
    result = tool._run()
    
    assert isinstance(result, str)
    assert "claim" in result.lower()
    assert "documents" in result.lower()