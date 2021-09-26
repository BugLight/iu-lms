from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class RoleEnum(str, Enum):
    admin = "admin"
    student = "student"
    teacher = "teacher"


class UserBase(BaseModel):
    name: str
    email: str
    birth_date: Optional[datetime] = None
    role: RoleEnum


class User(UserBase):
    id: UUID


class UserCreate(UserBase):
    pass
