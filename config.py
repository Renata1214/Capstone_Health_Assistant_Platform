# healthsync_ai/config.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass #Python decorator automatically writes an __init__ method  a __repr__ method
class Settings:
    supabase_url: str
    supabase_key: str
    openrouter_api_key: str
    model_name: str = "anthropic/claude-3.5-sonnet"

    @classmethod # method that: belongs to the class, not an individual object, receives cls instead of self
    def from_env(cls) -> "Settings":
        return cls(
            supabase_url=os.environ["SUPABASE_URL"],
            supabase_key=os.environ["SUPABASE_SERVICE_ROLE_KEY"],
            openrouter_api_key=os.environ["OPENROUTER_API_KEY"],
            model_name=os.getenv("MODEL_NAME", "anthropic/claude-3.5-sonnet"),
        )


settings = Settings.from_env()
