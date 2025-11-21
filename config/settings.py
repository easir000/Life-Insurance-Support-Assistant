from pydantic import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    openai_temperature: float = 0.3
    
    # Application Settings
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False
    
    # Database Settings
    database_url: str = "sqlite:///./insurance_agent.db"
    
    # Session Management
    session_timeout_minutes: int = 30
    max_session_history: int = 50
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Create logs directory if it doesn't exist
os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)