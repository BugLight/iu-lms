from typing import List, Optional

from pydantic import BaseModel

from gateway.schemas.task import Task
from gateway.schemas.user import User


class AcademicPerformanceReportRow(BaseModel):
    user: User
    scores: List[Optional[int]]


class AcademicPerformanceReport(BaseModel):
    tasks: List[Task]
    rows: List[AcademicPerformanceReportRow]
