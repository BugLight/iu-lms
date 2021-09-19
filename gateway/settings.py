from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    pass


@lru_cache
def get_settings():
    return Settings()
