from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Attempt(BaseModel):
    id: UUID
    created: datetime
    filename: Optional[str]
