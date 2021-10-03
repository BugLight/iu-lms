from datetime import datetime

from sqlalchemy import Column, ForeignKeyConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from tasks.models import Base
from tasks.models.assignment import Assignment
from tasks.proto import attempt_pb2


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(UUID(as_uuid=True), primary_key=True)
    task_id = Column(UUID(as_uuid=True), nullable=False)
    assignee_id = Column(UUID(as_uuid=True), nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        ForeignKeyConstraint((task_id, assignee_id), (Assignment.task_id, Assignment.assignee_id)),
    )

    def to_protobuf(self) -> attempt_pb2.AttemptResponse:
        return attempt_pb2.AttemptResponse(id=str(self.id),
                                           task_id=str(self.task_id),
                                           assignee_id=str(self.assignee_id),
                                           created=int(self.created.timestamp()))