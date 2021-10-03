from datetime import datetime
from enum import Enum
from typing import List, Union

from pydantic import BaseModel

from gateway.schemas.attempt import Attempt
from gateway.schemas.review import Review
from gateway.schemas.task import Task
from gateway.schemas.user import User


class HistoryRecordTypeEnum(str, Enum):
    ATTEMPT = "ATTEMPT"
    REVIEW = "REVIEW"


class HistoryRecord(BaseModel):
    type: HistoryRecordTypeEnum
    time: datetime
    record: Union[Attempt, Review]


class AssignmentStatusEnum(str, Enum):
    ASSIGNED = "ASSIGNED"
    ATTEMPT_UPLOADED = "ATTEMPT_UPLOADED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    APPROVED = "APPROVED"


class Assignment(BaseModel):
    created: datetime
    updated: datetime
    status: AssignmentStatusEnum
    score: int
    assignee: User


class AssignmentExtended(Assignment):
    task: Task
    history: List[HistoryRecord]
