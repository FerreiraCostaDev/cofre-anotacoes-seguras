import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "chave_fallback_caso_env_falhe")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

settings = Settings()