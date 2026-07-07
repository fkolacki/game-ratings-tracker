from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    rawg_api_key: str
    database_url: str
    
    model_config = {"env_file": ".env"}

settings = Settings()