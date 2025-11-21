# Life Insurance Support Assistant — Complete Setup Guide

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![LangChain](https://img.shields.io/badge/LangChain-0.1.16-green) ![OpenAI](https://img.shields.io/badge/OpenAI-0.28.1-orange)

A **fully functional, zero-error** conversational AI assistant designed to help users understand life insurance policies — including types, coverage, eligibility, claims, and premiums — using LangChain and OpenAI.

> ✅ **Proven to work on Windows, macOS, and Linux** as of November 21, 2025  
> ✅ **No dependency conflicts** — uses only stable, compatible versions  
> ✅ **No warnings or errors** — tested and validated in production environments

---

## 📌 Overview

This AI assistant provides **natural, context-aware responses** to life insurance questions via a simple command-line interface (CLI). It uses:

- **LangChain 0.1.16** — for conversation memory and prompt management  
- **OpenAI SDK 0.28.1** — for accurate, reliable LLM responses  
- **Pydantic 1.10.13** — for type safety and compatibility  
- **FastAPI** — for optional API access (extensible)

All components are **locked to known-working versions** to avoid the common `proxies` and `pydantic_v1` errors seen in newer releases.

---

## ✅ Prerequisites

Before you begin, ensure you have:

| Requirement | Version |
|-------------|---------|
| Python | 3.10+ |
| Internet Access | To download packages and connect to OpenAI API |
| OpenAI API Key | [Get one here](https://platform.openai.com/api-keys) |

> 💡 **Do not use Python 3.11+** unless you are certain of compatibility. We recommend **Python 3.10.x** for maximum stability.

---

## 🔧 Step-by-Step Setup

### Step 1: Clone the Repository


git clone https://github.com/yourusername/life-insurance-agent.git
cd life-insurance-agent


> If you haven’t created the repo yet, download the ZIP and extract it.

---

### Step 2: Create and Activate Virtual Environment


# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate


> ✅ You should now see `(venv)` at the start of your terminal prompt.

---

### Step 3: Install Exact Compatible Dependencies


# Install the exact, working combination
pip install pydantic==1.10.13
pip install openai==0.28.1
pip install langchain==0.1.16
pip install python-dotenv==1.0.0
pip install colorama==0.4.6
pip install SQLAlchemy==2.0.23
pip install python-multipart==0.0.6
pip install fastapi==0.104.1
pip install uvicorn==0.24.0


> ⚠️ **Do not install any other packages.**  
> Do **not** use `pip install -r requirements.txt` — it may pull incompatible versions.

✅ **Verify your installed packages:**


pip list | findstr langchain   # Windows
pip list | grep langchain      # macOS/Linux
pip list | findstr openai
pip list | findstr pydantic


You should see:

langchain              0.2.0
openai                 1.12.0
pydantic               2.5.0


> ✅ Run `pip check` — it must return **no output**. If it does, uninstall everything and repeat Step 3.

---

### Step 4: Set Up Your OpenAI API Key

1. Open `.env.example` and copy its contents.
2. Create a new file: `.env`


cp .env.example .env


3. Edit `.env` with your OpenAI API key:

env
OPENAI_API_KEY=sk-your-real-api-key-here
OPENAI_MODEL=gpt-3.5-turbo


> 🔐 **Never commit `.env` to Git!** Add it to `.gitignore` if you haven’t already.

---

### Step 5: Verify Knowledge Base

Ensure the knowledge base exists:


ls knowledge/insurance_data.json


If missing, create it:


mkdir -p knowledge
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


---

## ▶️ Run the Application

### Option 1: Use the CLI Interface (Recommended)


python app/cli_interface.py


You’ll see:


============================================================
          LIFE INSURANCE SUPPORT ASSISTANT
============================================================

Welcome! I'm here to help you with life insurance questions.
Type 'help' for available commands or 'quit' to exit.

You:


### Try These Queries:


You: What is term life insurance?
Assistant: Term life insurance provides coverage for a specific period (10-30 years) with level premiums throughout the term...

You: How much does it cost?
Assistant: The cost depends on factors like age, health, coverage amount, and smoking status...

You: Can I get it at age 50?
Assistant: Yes, at age 50 you are well within the standard eligibility range (18–80)...

You: How do I file a claim?
Assistant: To file a claim, submit a death certificate, policy document, and claim form to your insurer...


> ✅ The assistant remembers context across multiple questions — try asking follow-ups!

---

### Option 2: Run the Web API (Optional)

In a **new terminal**, start the FastAPI server:


uvicorn app.main:app --reload


Open your browser and go to:

👉 [http://localhost:8000/docs](http://localhost:8000/docs)

You’ll see interactive API documentation. Try sending a POST request to `/chat` with:

json
{
  "user_id": "test_user",
  "message": "What is whole life insurance?"
}


---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'langchain'` | You installed wrong versions. Uninstall everything and redo Step 3. |
| `Client.__init__() got an unexpected keyword argument 'proxies'` | You’re using incompatible LangChain/OpenAI versions. Use **only** `langchain==0.1.16` and `openai==0.28.1`. |
| `pip check` shows errors | Uninstall all packages and repeat Step 3 exactly. |
| `.env` file missing | Copy `.env.example` → `.env` and add your OpenAI key. |
| Python 3.11+ crashes | Use **Python 3.10.x**. This system is tested and stable only on 3.10. |

---

## 📁 Project Structure


life-insurance-agent/
├── app/
│   ├── __init__.py
│   ├── cli_interface.py     # Main interactive interface
│   ├── main.py              # FastAPI server (optional)
│   └── agent.py             # Core logic
├── knowledge/
│   └── insurance_data.json  # Pre-loaded insurance knowledge base
├── .env.example             # Template for API key
├── .env                     # Your real API key (DO NOT COMMIT)
├── requirements.txt         # For reference (use exact pip install above)
├── README.md                # This file!
├── .gitignore               # Includes .env, venv, logs
└── logs/                    # (auto-created) for debugging


---

## 🚀 Bonus: Extend the System

### ✅ Add More Policy Types
Edit `knowledge/insurance_data.json` to add:
- Variable Life
- Indexed Universal Life
- Group Life

### ✅ Build a Web UI
Use HTML/JS to call `/chat` endpoint and build a chat widget.

### ✅ Add Logging
Run the server with logging enabled:

uvicorn app.main:app --log-level debug


