from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    supabase_url: str
    supabase_service_key: str
    database_url: str = ""
    fmcsa_webkey: str = ""
    api_key: str = "hr-challenge"
    debug: bool = False
    log_level: str = "INFO"
    environment: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
