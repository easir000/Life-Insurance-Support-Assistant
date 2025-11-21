import httpx
from typing import Dict, Any, Optional
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models import MessageResponse

class InsuranceAPIClient:
    """
    Client for interacting with the life insurance support assistant API
    Useful for testing and integration
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=30.0)
    
    def chat(self, user_id: str, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a message to the chat endpoint"""
        response = self.client.post(
            f"{self.base_url}/chat",
            json={
                "user_id": user_id,
                "message": message,
                "session_id": session_id
            }
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the service"""
        response = self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a specific session"""
        response = self.client.get(f"{self.base_url}/sessions/{session_id}")
        response.raise_for_status()
        return response.json()
    
    def delete_session(self, session_id: str) -> Dict[str, Any]:
        """Delete a specific session"""
        response = self.client.delete(f"{self.base_url}/sessions/{session_id}")
        response.raise_for_status()
        return response.json()
    
    def get_policy_types(self) -> Dict[str, Any]:
        """Get available policy types"""
        response = self.client.get(f"{self.base_url}/knowledge/types")
        response.raise_for_status()
        return response.json()
    
    def close(self):
        """Close the client connection"""
        self.client.close()