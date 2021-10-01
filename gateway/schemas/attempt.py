from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Attempt(BaseModel):
    id: UUID
    created: datetime
    filename: str
