from langchain.tools import BaseTool
from typing import Optional, Type, Dict, Any
from pydantic import BaseModel, Field
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PolicyTypeInput(BaseModel):
    policy_type: str = Field(description="Type of life insurance policy to get information about")

class PolicyTypeTool(BaseTool):
    name = "get_policy_type_info"
    description = "Get detailed information about specific life insurance policy types"
    args_schema: Type[BaseModel] = PolicyTypeInput

    def _run(self, policy_type: str) -> str:
        """Get information about a specific policy type"""
        try:
            knowledge_base = self._load_knowledge_base()
            
            # Normalize input
            normalized_type = policy_type.lower().replace(" ", "_")
            
            if normalized_type in knowledge_base.get("policy_types", {}):
                info = knowledge_base["policy_types"][normalized_type]
                return f"""{info['description']}
                
Benefits: {', '.join(info['benefits'])}
Duration: {info['duration']}
Eligibility: {info['eligibility']}"""
            else:
                available_types = list(knowledge_base.get("policy_types", {}).keys())
                return f"""I couldn't find information about '{policy_type}' specifically.
Available policy types include: {', '.join(available_types)}."""
                
        except Exception as e:
            logger.error(f"Error retrieving policy type info: {str(e)}")
            return "An error occurred while retrieving policy information. Please try again."
    
    def _load_knowledge_base(self) -> dict:
        """Load knowledge base from file"""
        try:
            with open("knowledge/insurance_data.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Knowledge base file not found")
            return {"policy_types": {}}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in knowledge base: {str(e)}")
            return {"policy_types": {}}

class EligibilityInput(BaseModel):
    age: Optional[int] = Field(None, description="User's age")
    health_status: Optional[str] = Field(None, description="Health status description")

class EligibilityTool(BaseTool):
    name = "check_eligibility"
    description = "Check basic eligibility requirements for life insurance"
    args_schema: Type[BaseModel] = EligibilityInput

    def _run(self, age: Optional[int] = None, health_status: Optional[str] = None) -> str:
        """Return eligibility information based on user inputs"""
        try:
            knowledge_base = self._load_common_questions()
            
            # Start with general requirements
            response_parts = [
                "Life insurance eligibility typically depends on several factors:"
            ]
            
            # Age requirements
            if age is not None:
                if age < 18:
                    response_parts.append(f"- Age: You must be at least 18 years old to qualify. Current age: {age}")
                elif age > 80:
                    response_parts.append(f"- Age: Most policies are not available after age 80. Current age: {age}")
                else:
                    response_parts.append(f"- Age: Qualifies within standard range (18-80 years). Current age: {age}")
            else:
                response_parts.append("- Age: Typically 18-80 years old")
            
            # Health requirements
            if health_status:
                response_parts.append(f"- Health status: {health_status}")
            else:
                response_parts.append("- Health status: Medical examination required")
            
            # Other requirements
            response_parts.extend([
                "- Medical history: Full disclosure required",
                "- Lifestyle factors: Smoking, alcohol consumption, etc.",
                "- Financial stability: Proof of insurable interest needed",
                "- Occupation risk level: Higher risk occupations may have restrictions"
            ])
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Error checking eligibility: {str(e)}")
            return "An error occurred while checking eligibility. Please provide your age and health status."
    
    def _load_common_questions(self) -> dict:
        """Load common questions from knowledge base"""
        try:
            with open("knowledge/insurance_data.json", "r") as f:
                data = json.load(f)
                return data.get("common_questions", {})
        except:
            return {}

class ClaimsProcessInput(BaseModel):
    pass

class ClaimsProcessTool(BaseTool):
    name = "get_claims_process"
    description = "Get information about the life insurance claims process"
    args_schema: Type[BaseModel] = ClaimsProcessInput

    def _run(self, **kwargs) -> str:
        """Return claims process information"""
        try:
            knowledge_base = self._load_claims_info()
            
            required_docs = ", ".join(knowledge_base.get("required_documents", []))
            
            return f"""The life insurance claims process involves these steps:

1. Notify the insurance company of the policyholder's death
2. Submit the following documents:
   - {required_docs}

3. The claim will be reviewed (typically takes {knowledge_base.get('processing_time', '30-60 days')})
4. Upon approval, the death benefit will be paid to beneficiaries

Contact your insurance provider directly to initiate the claims process."""
                
        except Exception as e:
            logger.error(f"Error retrieving claims process: {str(e)}")
            return "An error occurred while retrieving claims information."
    
    def _load_claims_info(self) -> dict:
        """Load claims information from knowledge base"""
        try:
            with open("knowledge/insurance_data.json", "r") as f:
                data = json.load(f)
                return data.get("common_questions", {}).get("claims_process", {})
        except:
            return {
                "required_documents": ["Death certificate", "Policy document", "Claim form"],
                "processing_time": "30-60 days"
            }

# List of all tools
TOOLS = [
    PolicyTypeTool(),
    EligibilityTool(),
    ClaimsProcessTool()
]