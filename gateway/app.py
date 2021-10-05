from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gateway.routers import (
    courses,
    users,
    tasks
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://iulms.ml",
        "https://api.iulms.ml",
        "http://localhost",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(courses.router)
app.include_router(users.router)
app.include_router(tasks.router)


@app.get("/health")
async def health():
    return "Healthy"
