from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gateway.routers import (
    courses,
    users
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(courses.router)
app.include_router(users.router)


@app.get("/health")
async def health():
    return "Healthy"
