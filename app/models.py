from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

class MessageRequest(BaseModel):
    """
    Request model for chat endpoint
    """
    user_id: str
    message: str
    session_id: Optional[str] = None

class MessageResponse(BaseModel):
    """
    Response model for chat endpoint
    """
    response: str
    session_id: str
    context: Dict[str, Any] = {}
    timestamp: datetime = datetime.now()
    query_type: Optional[str] = None

class HealthStatus(BaseModel):
    """
    Health check response model
    """
    status: str
    service: str
    timestamp: datetime = datetime.now()
    version: str = "0.1.0"

class KnowledgeBaseEntry(BaseModel):
    """
    Model for knowledge base entries
    """
    category: str
    subcategory: str
    content: str
    last_updated: datetime = datetime.now()

class SessionInfo(BaseModel):
    """
    Model for session information
    """
    session_id: str
    user_id: str
    created_at: datetime
    last_active: datetime
    message_count: int
    context_summary: str