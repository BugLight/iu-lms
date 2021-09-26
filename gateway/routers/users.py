import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Body, HTTPException

from gateway.dependencies.page_flags import PageFlags
from gateway.schemas.page import Page
from gateway.schemas.user import User, UserCreate, RoleEnum

router = APIRouter(prefix="/users", tags=["users"])
users = [
    User(name="Admin",
         role="admin",
         id=UUID("d438a258-f8aa-477e-bb91-0d921b72ac70"),
         email="admin@iulms.ml",
         birth_date=datetime.fromisoformat("1999-05-21")),
    User(name="John", role="student", id=UUID("86ca2ae7-238b-493b-94eb-c16e24adc789"), email="john@iulms.ml"),
    User(name="Alice", role="teacher", id=UUID("3b31a401-32a9-49c1-8e9c-b44ed2d18a1e"), email="alice@iulms.ml"),
    User(name="Bob", role="student", id=UUID("ed6453c2-f97f-458f-93cd-55dcbf7072e2"), email="bob@iulms.ml"),
    User(name="Felix", role="teacher", id=UUID("613ddddb-4080-4040-93cc-7e022dcbe6b4"), email="felix@iulms.ml")
]


@router.get("/", response_model=Page[User])
async def get_users(role: Optional[RoleEnum] = None, name: Optional[str] = None, page_flags: PageFlags = Depends()):
    results = users[:]
    if role:
        results = list(filter(lambda u: u.role == role, results))
    if name:
        results = list(filter(lambda u: u.name.lower().startswith(name.lower()), results))
    page = results[page_flags.offset:page_flags.offset + page_flags.limit]
    return Page(results=page,
                total_count=len(results),
                offset=page_flags.offset)


@router.get("/{id}", response_model=User)
async def get_user_by_id(id: UUID):
    found = filter(lambda u: u.id == id, users)
    for user in found:
        return user
    raise HTTPException(status_code=404, detail="Not found")


@router.post("/", response_model=User, status_code=201)
async def create_user(user_create: UserCreate):
    user = User(id=uuid.uuid4(), **user_create.dict())
    users.append(user)
    return user


@router.post("/auth")
async def auth(login: str = Body(...), password: str = Body(...)):
    if login == "admin" and password == "admin":
        return {
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJkNDM4YTI1OC1mOGFhLTQ3N2UtYmI5MS0wZDkyMWI3MmFjNzAiLCJuYW1lIjoiQWRtaW4iLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3MzI0OTAxMzJ9.LkSEDbyfF2mkx3eblyS3-nRfYeszfM6tYkvqEsR7CKI"
        }
    raise HTTPException(status_code=401, detail="Incorrect login or password")
