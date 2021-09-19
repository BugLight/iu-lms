from fastapi import FastAPI
from gateway.routers import (
    courses,
    tasks,
    users
)

app = FastAPI()

app.include_router(courses.router)
app.include_router(tasks.router)
app.include_router(users.router)
