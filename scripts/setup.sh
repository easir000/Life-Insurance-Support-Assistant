#!/bin/bash

echo "Setting up Life Insurance Support Assistant..."

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p knowledge

# Create example environment file if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env file - please add your OpenAI API key"
fi

# Create knowledge base if it doesn't exist
if [ ! -f "knowledge/insurance_data.json" ]; then
    echo "Creating knowledge base..."
    cat > knowledge/insurance_data.json << 'EOF'
{
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
EOF
fi

echo "Setup complete!"
echo "To install dependencies: pip install -r requirements.txt"
echo "To run the server: uvicorn app.main:app --reload"
echo "To run the CLI: python app/cli_interface.py"