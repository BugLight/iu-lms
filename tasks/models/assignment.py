import enum
from datetime import datetime

from sqlalchemy import Column, ForeignKey, DateTime, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID

from tasks.models import Base
from tasks.models.task import Task
from tasks.proto import assignment_pb2


class AssignmentStatusEnum(str, enum.Enum):
    ASSIGNED = "ASSIGNED"
    ATTEMPT_UPLOADED = "ATTEMPT_UPLOADED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    APPROVED = "APPROVED"


class Assignment(Base):
    __tablename__ = "assignments"

    task_id = Column(UUID(as_uuid=True), ForeignKey(Task.id), primary_key=True)
    assignee_id = Column(UUID(as_uuid=True), primary_key=True)
    created = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(Enum(AssignmentStatusEnum), nullable=False, default=AssignmentStatusEnum.ASSIGNED)
    score = Column(Integer, nullable=False, default=0)

    def to_protobuf(self) -> assignment_pb2.AssignmentResponse:
        return assignment_pb2.AssignmentResponse(task_id=str(self.task_id),
                                                 assignee_id=str(self.assignee_id),
                                                 created=int(self.created.timestamp()),
                                                 updated=int(self.updated.timestamp()),
                                                 status=self.status,
                                                 score=self.score)
