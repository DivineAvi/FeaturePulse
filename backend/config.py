import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Database Configuration
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    
    # Slack Configuration
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")
    
    # Tracking Configuration
    MAX_PAGES_PER_SITE: int = int(os.getenv("MAX_PAGES_PER_SITE", "10"))
    MAX_SOCIAL_POSTS: int = int(os.getenv("MAX_SOCIAL_POSTS", "10"))
    
    # Schedule Configuration
    WEEKLY_RUN_DAY: str = os.getenv("WEEKLY_RUN_DAY", "monday")  # day of week
    WEEKLY_RUN_TIME: str = os.getenv("WEEKLY_RUN_TIME", "09:00")  # HH:MM format
    
    # Error Handling
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY_SECONDS: int = int(os.getenv("RETRY_DELAY_SECONDS", "60"))

CONFIG = Config()