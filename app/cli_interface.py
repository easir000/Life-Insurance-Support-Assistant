import asyncio
import sys
from typing import Optional
import os
import json
from colorama import init, Fore, Style
from datetime import datetime
import uuid

# Add project root to Python path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ✅ CORRECT IMPORTS FOR LANGCHAIN 0.2.x
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain.chains import create_history_aware_retriever, create_retrieval_chain
# from langchain.chains.history_aware_retriever import create_history_aware_retriever
# from langchain.chains.retrieval import create_retrieval_chain
# from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
SESSION_TIMEOUT_MINUTES = 30

# Set API key as environment variable
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

class MessageResponse:
    """Simple response model for CLI"""
    def __init__(self, response: str, session_id: str, context: dict = None, query_type: str = None):
        self.response = response
        self.session_id = session_id
        self.context = context or {}
        self.query_type = query_type
        self.timestamp = datetime.now()

class InsuranceAgent:
    """
    Main AI agent for life insurance support — using LangChain 0.2.x
    """
    
    def __init__(self):
        self.sessions = {}
        self.knowledge_base = self._load_knowledge_base()
        
        # ✅ Initialize LLM with LangChain 0.2.x syntax
        self.llm = ChatOpenAI(
            model=OPENAI_MODEL,
            temperature=0.3,
            max_tokens=1000,
        )
        
        # Define system prompt
        self.system_prompt = """You are a helpful life insurance support assistant. Provide accurate information about:
        - Life insurance policy types (Term, Whole Life, Universal Life, etc.)
        - Coverage options and benefits
        - Eligibility requirements
        - Claims process
        - Premium calculations
        - Policy riders and add-ons
        
        Always provide clear, professional, and accurate information. If unsure, acknowledge the limitation."""
    
    def _load_knowledge_base(self):
        """Load knowledge base from JSON file"""
        try:
            with open("knowledge/insurance_data.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
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
                    }
                }
            }
    
    def _get_or_create_session(self, session_id, user_id):
        """Get existing session or create new one"""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if session_id not in self.sessions:
            # ✅ Use ChatMessageHistory for LangChain 0.2.x
            self.sessions[session_id] = {
                "user_id": user_id,
                "created_at": datetime.now(),
                "last_active": datetime.now(),
                "message_count": 0,
                "history": ChatMessageHistory()
            }
        
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
        else:
            return "general"
    
    def process_message(self, user_id: str, message: str, session_id: str = None):
        """Process user message and return response"""
        # Get or create session
        session_id = self._get_or_create_session(session_id, user_id)
        session_data = self.sessions[session_id]
        
        # Update message count
        session_data["message_count"] += 1
        
        # Classify query
        query_type = self._classify_query(message)
        
        # ✅ Create prompt for LangChain 0.2.x
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        # ✅ Create conversation chain for LangChain 0.2.x
        from langchain_core.runnables import RunnableLambda
        
        def get_session_history(session_id: str):
            return self.sessions[session_id]["history"]
        
        # Create chain
        chain = prompt | self.llm
        
        # Add message to history
        session_data["history"].add_user_message(message)
        
        # Generate response
        response = chain.invoke({
            "input": message,
            "history": session_data["history"].messages
        })
        
        response_text = response.content
        
        # Add AI response to history
        session_data["history"].add_ai_message(response_text)
        
        # Create response object
        response_obj = MessageResponse(
            response=response_text,
            session_id=session_id,
            context={
                "query_type": query_type,
                "message_count": session_data["message_count"]
            },
            query_type=query_type
        )
        
        return response_obj

# CLI Interface class (unchanged)
class CLIInterface:
    """
    Command-line interface for the life insurance support assistant
    Provides an interactive way to test the agent
    """
    
    def __init__(self):
        self.agent = InsuranceAgent()
        self.current_session_id: Optional[str] = None
        self.user_id = "cli_user"
        self.running = True
    
    def display_welcome(self):
        """Display welcome message and instructions"""
        print(Fore.CYAN + "="*60)
        print(Fore.CYAN + "          LIFE INSURANCE SUPPORT ASSISTANT")
        print(Fore.CYAN + "="*60)
        print()
        print(Fore.YELLOW + "Welcome! I'm here to help you with life insurance questions.")
        print(Fore.YELLOW + "Type 'help' for available commands or 'quit' to exit.")
        print()
    
    def display_help(self):
        """Display help information"""
        print("\n" + Fore.GREEN + "Available Commands:")
        print(Fore.WHITE + "  help           - Show this help message")
        print(Fore.WHITE + "  quit           - Exit the application")
        print(Fore.WHITE + "  new            - Start a new conversation")
        print(Fore.WHITE + "  session        - Show current session info")
        print(Fore.WHITE + "  policy types   - List available policy types")
        print(Fore.WHITE + "  clear          - Clear screen")
        print()
        print(Fore.GREEN + "Example Questions:")
        print(Fore.WHITE + "  What is term life insurance?")
        print(Fore.WHITE + "  How do I file a claim?")
        print(Fore.WHITE + "  Am I eligible at age 45?")
        print()
    
    def display_session_info(self):
        """Display current session information"""
        if self.current_session_id and self.current_session_id in self.agent.sessions:
            session_data = self.agent.sessions[self.current_session_id]
            print(Fore.CYAN + "\nCurrent Session:")
            print(Fore.WHITE + f"  ID: {self.current_session_id}")
            print(Fore.WHITE + f"  Created: {session_data['created_at']}")
            print(Fore.WHITE + f"  Messages: {session_data['message_count']}")
            print(Fore.WHITE + f"  Duration: {(session_data['last_active'] - session_data['created_at']).seconds} seconds")
        else:
            print(Fore.YELLOW + "\nNo active session")
    
    def get_policy_types(self):
        """Display available policy types"""
        policy_types = list(self.agent.knowledge_base.get("policy_types", {}).keys())
        print(Fore.CYAN + "\nAvailable Policy Types:")
        for pt in policy_types:
            formatted = pt.replace("_", " ").title()
            print(Fore.WHITE + f"  • {formatted}")
    
    def clear_screen(self):
        """Clear the terminal screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        self.display_welcome()
    
    def start_conversation(self):
        """Start the interactive conversation loop"""
        self.display_welcome()
        
        while self.running:
            try:
                user_input = input(Fore.BLUE + "You: " + Style.RESET_ALL).strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() == 'quit':
                    self.quit()
                elif user_input.lower() == 'help':
                    self.display_help()
                elif user_input.lower() == 'new':
                    self.start_new_conversation()
                elif user_input.lower() == 'session':
                    self.display_session_info()
                elif user_input.lower() == 'policy types':
                    self.get_policy_types()
                elif user_input.lower() == 'clear':
                    self.clear_screen()
                else:
                    # Process regular message
                    self.process_message(user_input)
                    
            except KeyboardInterrupt:
                print(Fore.YELLOW + "\n\nGoodbye!")
                sys.exit(0)
            except EOFError:
                print(Fore.YELLOW + "\n\nGoodbye!")
                sys.exit(0)
            except Exception as e:
                print(Fore.RED + f"An error occurred: {str(e)}")
                import traceback
                traceback.print_exc()
    
    def process_message(self, message: str):
        """Process a user message and display response"""
        try:
            response = self.agent.process_message(
                user_id=self.user_id,
                message=message,
                session_id=self.current_session_id
            )
            
            # Update session ID if new one was created
            if self.current_session_id != response.session_id:
                self.current_session_id = response.session_id
            
            # Display response
            print(Fore.GREEN + f"Assistant: " + Fore.WHITE + f"{response.response}")
            print()
            
        except Exception as e:
            print(Fore.RED + f"Error: {str(e)}")
            print()
    
    def start_new_conversation(self):
        """Start a new conversation with a new session"""
        self.current_session_id = None
        print(Fore.YELLOW + "Started a new conversation.")
        print()
    
    def quit(self):
        """Quit the application"""
        print(Fore.YELLOW + "Thank you for using Life Insurance Support Assistant. Goodbye!")
        self.running = False
        sys.exit(0)

def main():
    """Main entry point for CLI interface"""
    try:
        cli = CLIInterface()
        cli.start_conversation()
    except Exception as e:
        print(Fore.RED + f"Application error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()