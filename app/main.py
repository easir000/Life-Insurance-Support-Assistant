from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from config.settings import settings
from .models import MessageRequest, MessageResponse, HealthStatus
from .agent import InsuranceAgent

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("Starting Life Insurance Support Assistant...")
    try:
        global insurance_agent
        insurance_agent = InsuranceAgent()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Life Insurance Support Assistant...")

# Create FastAPI app
app = FastAPI(
    title="Life Insurance Support Assistant",
    description="A conversational AI agent for life insurance inquiries",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
insurance_agent: Optional[InsuranceAgent] = None

@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint"""
    try:
        status_msg = "healthy"
        if insurance_agent is None:
            status_msg = "unhealthy - agent not initialized"
            raise HTTPException(status_code=503, detail="Agent not initialized")
            
        return HealthStatus(status=status_msg, service="Life Insurance Support Assistant")
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/chat", response_model=MessageResponse)
async def chat_endpoint(request: MessageRequest):
    """Process user message and return response"""
    try:
        if insurance_agent is None:
            raise HTTPException(status_code=503, detail="Service unavailable")
        
        response = insurance_agent.process_message(
            user_id=request.user_id,
            message=request.message,
            session_id=request.session_id
        )
        
        return response
        
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get information about a specific session"""
    try:
        if insurance_agent is None or session_id not in insurance_agent.sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = insurance_agent.sessions[session_id]
        return {
            "session_id": session_id,
            "user_id": session_data["user_id"],
            "created_at": session_data["created_at"],
            "last_active": session_data["last_active"],
            "message_count": session_data["message_count"],
            "context_summary": str(session_data["context"])[:200] + "..." if session_data["context"] else ""
        }
    except Exception as e:
        logger.error(f"Error retrieving session info: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a specific session"""
    try:
        if insurance_agent is None or session_id not in insurance_agent.sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        del insurance_agent.sessions[session_id]
        return {"status": "deleted", "session_id": session_id}
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/knowledge/types")
async def get_policy_types():
    """Get available policy types"""
    try:
        if insurance_agent is None:
            raise HTTPException(status_code=503, detail="Service unavailable")
        
        policy_types = list(insurance_agent.knowledge_base.get("policy_types", {}).keys())
        return {"policy_types": policy_types}
    except Exception as e:
        logger.error(f"Error retrieving policy types: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")