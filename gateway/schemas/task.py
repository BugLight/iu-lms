from uuid import UUID

from pydantic import BaseModel

from gateway.schemas.course import Course
from gateway.schemas.user import User


class TaskBase(BaseModel):
    name: str
    description: str


class Task(TaskBase):
    id: UUID
    author: User
    course: Course


class TaskCreate(TaskBase):
    course_id: UUID
