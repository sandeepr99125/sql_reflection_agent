import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    
    PRIMARY_MODEL: str = "gemini-3.6-flash"
    
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    # openrouter/free automatically routes to any currently working free endpoint
    OPENROUTER_MODEL: str = "openrouter/free"

    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY and not cls.OPENROUTER_API_KEY:
            raise ValueError("At least one API key must be set in .env.")