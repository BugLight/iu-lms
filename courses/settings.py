from pydantic import BaseSettings, AnyUrl


class CoursesSettings(BaseSettings):
    POSTGRES_URI: AnyUrl

    class Config:
        env_prefix = "COURSES_"
        env_file = "courses/.env"


settings = CoursesSettings()
