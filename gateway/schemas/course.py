from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from gateway.schemas.user import User


class CourseBase(BaseModel):
    name: str
    description: Optional[str] = None


class CourseCreate(CourseBase):
    pass


class Course(CourseBase):
    id: UUID
    author: User
