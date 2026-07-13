from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    secret_key: str
    rawg_api_key: str
    database_url: str
    
    model_config = {"env_file": os.environ.get("ENV_FILE", ".env")}

settings = Settings()