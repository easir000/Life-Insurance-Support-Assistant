from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.chains import ConversationChain, LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate
)
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.schema import SystemMessage, HumanMessage
from typing import Dict, Any, Optional
import uuid
import json
import logging
from datetime import datetime, timedelta
from functools import lru_cache

from config.settings import settings
from .tools import TOOLS
from .models import MessageResponse

logger = logging.getLogger(__name__)

class InsuranceAgent:
    """
    Main AI agent for life insurance support
    Handles conversation management, context preservation, and response generation
    """
    
    def __init__(self):
        # Set OpenAI API key
        import os
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        
        self.llm = self._initialize_llm()
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.knowledge_base = self._load_knowledge_base()
        
        # Initialize agent with tools
        self.agent_executor = self._create_agent_executor()
        
        logger.info("InsuranceAgent initialized successfully")
    
    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize the LLM with configuration settings"""
        try:
            llm = ChatOpenAI(
                model_name=settings.openai_model,
                temperature=settings.openai_temperature
            )
            return llm
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load and cache the knowledge base"""
        try:
            with open("knowledge/insurance_data.json", "r") as f:
                data = json.load(f)
                logger.info("Knowledge base loaded successfully")
                return data
        except FileNotFoundError:
            logger.warning("Knowledge base file not found, using default data")
            return self._get_default_knowledge_base()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in knowledge base: {str(e)}")
            return self._get_default_knowledge_base()
    
    def _get_default_knowledge_base(self) -> Dict[str, Any]:
        """Return default knowledge base when file is missing"""
        return {
            "policy_types": {
                "term_life": {
                    "description": "Provides coverage for a specific term period (10-30 years)",
                    "benefits": ["Affordable premiums", "Pure death benefit", "Flexible term lengths"],
                    "eligibility": "Generally available up to age 80",
                    "duration": "Fixed term (10, 15, 20, 25, 30 years)"
                },
                "whole_life": {
                    "description": "Permanent coverage with guaranteed cash value component",
                    "benefits": ["Lifelong coverage", "Cash value accumulation", "Dividends (if applicable)"],
                    "eligibility": "Available up to age 75",
                    "duration": "Lifelong"
                },
                "universal_life": {
                    "description": "Flexible premium permanent life insurance with adjustable death benefit",
                    "benefits": ["Flexible premiums", "Adjustable coverage", "Cash value growth"],
                    "eligibility": "Available up to age 70",
                    "duration": "Lifelong"
                }
            },
            "common_questions": {
                "eligibility": {
                    "age_requirements": "Typically 18-80 years old",
                    "health_requirements": "Medical examination required",
                    "income_requirements": "Proof of insurable interest needed"
                },
                "claims_process": {
                    "required_documents": ["Death certificate", "Policy document", "Claim form", "Medical records"],
                    "processing_time": "Usually 30-60 days after receiving complete documentation",
                    "contact": "Contact your insurance company directly to initiate claims"
                },
                "premium_calculation": {
                    "factors": ["Age", "Gender", "Health status", "Smoking status", "Coverage amount", "Policy type"]
                }
            }
        }
    
    def _create_agent_executor(self) -> AgentExecutor:
        """Create the agent executor with tools and prompt"""
        try:
            # Define the prompt template
            system_prompt = """You are a knowledgeable and professional life insurance support assistant.
Your role is to provide accurate, helpful, and clear information about life insurance products and services.

Guidelines:
1. Always be truthful and admit when you don't know something
2. Provide concise but comprehensive answers
3. Use plain language that's easy to understand
4. Be empathetic and professional in tone
5. When appropriate, suggest consulting with a licensed insurance professional

Available Tools:
- get_policy_type_info: Get details about specific policy types
- check_eligibility: Check eligibility requirements
- get_claims_process: Get information about claims process

Use tools when they can provide more accurate information. Always maintain conversation context."""

            prompt = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])
            
            # Create the agent
            agent = create_openai_functions_agent(
                llm=self.llm,
                tools=TOOLS,
                prompt=prompt
            )
            
            # Create the agent executor
            agent_executor = AgentExecutor(
                agent=agent,
                tools=TOOLS,
                verbose=settings.debug,
                handle_parsing_errors=True
            )
            
            return agent_executor
            
        except Exception as e:
            logger.error(f"Failed to create agent executor: {str(e)}")
            raise
    
    def _get_or_create_session(self, session_id: Optional[str], user_id: str) -> str:
        """Get existing session or create new one"""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "user_id": user_id,
                "created_at": datetime.now(),
                "last_active": datetime.now(),
                "message_count": 0,
                "memory": ConversationBufferMemory(return_messages=True),
                "context": {}
            }
            logger.debug(f"Created new session: {session_id}")
        else:
            self.sessions[session_id]["last_active"] = datetime.now()
            logger.debug(f"Using existing session: {session_id}")
        
        return session_id
    
    def _classify_query(self, query: str) -> str:
        """Classify the type of insurance query"""
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ["term", "policy type", "coverage type", "difference between"]):
            return "policy_type"
        elif any(keyword in query_lower for keyword in ["eligibility", "qualify", "requirement", "can i get", "am i eligible"]):
            return "eligibility"
        elif any(keyword in query_lower for keyword in ["claim", "file", "payout", "death benefit", "submit"]):
            return "claims"
        elif any(keyword in query_lower for keyword in ["benefit", "coverage", "what does", "include", "covered"]):
            return "benefits"
        elif any(keyword in query_lower for keyword in ["cost", "price", "premium", "how much"]):
            return "cost"
        elif any(keyword in query_lower for keyword in ["compare", "vs", "versus"]):
            return "comparison"
        else:
            return "general"
    
    def _cleanup_old_sessions(self):
        """Remove expired sessions"""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            last_active = session_data["last_active"]
            if (now - last_active).total_seconds() > (settings.session_timeout_minutes * 60):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.debug(f"Removed expired session: {session_id}")
    
    def process_message(self, user_id: str, message: str, session_id: Optional[str] = None) -> MessageResponse:
        """
        Process user message and return response
        """
        try:
            # Clean up old sessions
            self._cleanup_old_sessions()
            
            # Validate input
            if not message or not message.strip():
                raise ValueError("Message cannot be empty")
            
            # Get or create session
            session_id = self._get_or_create_session(session_id, user_id)
            session_data = self.sessions[session_id]
            
            # Update message count
            session_data["message_count"] += 1
            
            # Classify query
            query_type = self._classify_query(message)
            
            # Prepare input for agent
            agent_input = {
                "input": message,
                "chat_history": session_data["memory"].chat_memory.messages
            }
            
            # Generate response using agent
            try:
                result = self.agent_executor.invoke(agent_input)
                response_text = result["output"]
            except Exception as e:
                logger.error(f"Agent execution failed: {str(e)}")
                response_text = "I apologize, but I'm having trouble processing your request. Please try again or rephrase your question."
            
            # Save conversation to memory
            session_data["memory"].save_context(
                {"input": message},
                {"output": response_text}
            )
            
            # Create response object
            response = MessageResponse(
                response=response_text,
                session_id=session_id,
                context={
                    "query_type": query_type,
                    "message_count": session_data["message_count"],
                    "session_duration": (datetime.now() - session_data["created_at"]).total_seconds()
                },
                query_type=query_type
            )
            
            logger.info(f"Processed message - User: {user_id}, Session: {session_id}, Query Type: {query_type}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise