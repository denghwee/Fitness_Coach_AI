import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ===== APP =====
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5001))
    DEBUG = FLASK_ENV == "development"

    # ===== PATHS =====
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.getenv(
        "DATA_DIR",
        os.path.join(BASE_DIR, "app", "data")
    )

    # ===== LLM =====
    LLM_PROVIDER = os.get_env("LLM_PROVIDER", "openai")

    # ===== OPENAI =====
    OPEN_API_KEY = os.get_env("OPEN_AI_KEY")
    OPENAI_MODEL = os.get_env("OPENAI_MODEL", "gpt-4o-mini")

    # ===== OLLAMA =====
    OLLAMA_MODEL = os.get_env("OLLAMA_MODEL", "llama3.1")
    OLLAMA_BASE_URL = os.get_env("OLLAMA_BASE_URL", "http://localhost:11434")

    # ===== AGENT SETTINGS =====
    DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", 0.3))