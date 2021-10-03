from datetime import date
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class RoleEnum(str, Enum):
    admin = "admin"
    student = "student"
    teacher = "teacher"


class UserBase(BaseModel):
    name: str
    email: EmailStr
    birth_date: Optional[date] = None
    role: RoleEnum


class User(UserBase):
    id: UUID


class UserCreate(UserBase):
    pass
