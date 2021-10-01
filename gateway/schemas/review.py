from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from gateway.schemas.user import User


class ReviewBase(BaseModel):
    approved: bool
    comment: Optional[str]
    score: Optional[int]


class Review(ReviewBase):
    id: UUID
    created: datetime
    author: User


class ReviewCreate(ReviewBase):
    pass
