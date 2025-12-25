import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ===== APP =====
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5003))
    DEBUG = FLASK_ENV == "development"

    # ===== PATHS =====
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.getenv(
        "DATA_DIR",
        os.path.join(BASE_DIR, "app", "data")
    )

    # ===== LLM =====
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

    # ===== RAG =====
    DB_TYPE = os.getenv("DB_TYPE", "chroma")
    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai")

    # ===== OPENAI =====
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # ===== OLLAMA =====
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # ===== AGENT SETTINGS =====
    DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", 0.3))
    # JWT
    SECRET_KEY = "kfhsk3jh2k3hk2h3k2h3k2h3h23jh23j423423"
    JWT_SECRET_KEY = "Some_super_secure_and_long_base64_encoded_secret_key_for_JSWT123"
    JWT_ALGORITHM = "HS256"
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    JWT_ACCESS_TOKEN_EXPIRES = False