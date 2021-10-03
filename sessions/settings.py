from pydantic import BaseSettings, EmailStr, AnyUrl


class SessionsSettings(BaseSettings):
    POSTGRES_URI: AnyUrl

    PASSWORD_SALT: str = ""
    PASSWORD_DEFAULT_LENGTH: int = 8

    JWT_SECRET: str
    JWT_LIFETIME: int = 3600

    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_LOGIN: str
    SMTP_PASSWORD: str
    SMTP_FROM: EmailStr

    class Config:
        env_prefix = "SESSIONS_"
        env_file = "sessions/.env"


settings = SessionsSettings()
