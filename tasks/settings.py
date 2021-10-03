from pydantic import BaseSettings, AnyUrl


class TasksSettings(BaseSettings):
    POSTGRES_URI: AnyUrl

    class Config:
        env_prefix = "TASKS_"
        env_file = "tasks/.env"


settings = TasksSettings()
