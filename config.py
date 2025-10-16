import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    API_HOST = os.getenv("API_HOST", "127.0.0.1")
    API_PORT = int(os.getenv("API_PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # GitHub Configuration
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN environment variable is required")
    
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
    if not GITHUB_USERNAME:
        raise ValueError("GITHUB_USERNAME environment variable is required")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    # Security
    ALLOWED_SECRETS = [s.strip() for s in os.getenv("ALLOWED_SECRETS", "").split(",") if s.strip()]
    
    # Evaluation
    MAX_RETRIES = 5
    RETRY_DELAYS = [1, 2, 4, 8, 16]
    
    # File paths
    LOG_DIR = "logs"
    ATTACHMENTS_DIR = "attachments"
    
    # Timeouts
    DEPLOYMENT_TIMEOUT = 600  # 10 minutes
    EVALUATION_TIMEOUT = 30

config = Config()
