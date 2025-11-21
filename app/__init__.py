"""
Life Insurance Support Assistant - Main Package
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main components for easier access
from .agent import InsuranceAgent
from .models import MessageRequest, MessageResponse, HealthStatus
from .tools import TOOLS

__all__ = [
    'InsuranceAgent',
    'MessageRequest',
    'MessageResponse',
    'HealthStatus',
    'TOOLS'
]