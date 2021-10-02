from pydantic import BaseSettings, AnyUrl


class SessionsSettings(BaseSettings):
    POSTGRES_URI: AnyUrl

    class Config:
        env_prefix = "COURSES_"
        env_file = ".env"


settings = SessionsSettings()
