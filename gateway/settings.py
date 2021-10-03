from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    SESSIONS_HOST: str
    COURSES_HOST: str

    class Config:
        env_prefix = "GATEWAY_"
        env_file = "gateway/.env"


@lru_cache
def get_settings():
    return Settings()
