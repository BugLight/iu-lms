from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    SESSIONS_HOST: str
    SESSIONS_PORT: int
    COURSES_HOST: str
    COURSES_PORT: int
    TASKS_HOST: str
    TASKS_PORT: int

    GRPC_CACHE_ENABLED: bool = False
    GRPC_CACHE_MAX_SIZE: float = 128
    GRPC_CACHE_TTL: float = 120

    class Config:
        env_prefix = "GATEWAY_"
        env_file = "gateway/.env"


@lru_cache
def get_settings():
    return Settings()
