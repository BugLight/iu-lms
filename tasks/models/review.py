import uuid
from datetime import datetime

from sqlalchemy import Column, ForeignKeyConstraint, Boolean, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from tasks.models import Base
from tasks.models.assignment import Assignment
from tasks.proto import review_pb2


class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), nullable=False)
    assignee_id = Column(UUID(as_uuid=True), nullable=False)
    author_id = Column(UUID(as_uuid=True), nullable=False)
    approved = Column(Boolean, nullable=False, default=False)
    comment = Column(String)
    score = Column(Integer)
    created = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        ForeignKeyConstraint((task_id, assignee_id), (Assignment.task_id, Assignment.assignee_id)),
    )

    def to_protobuf(self) -> review_pb2.ReviewResponse:
        return review_pb2.ReviewResponse(id=str(self.id),
                                         task_id=str(self.task_id),
                                         assignee_id=str(self.assignee_id),
                                         author_id=str(self.author_id),
                                         approved=self.approved,
                                         comment=self.comment,
                                         score=self.score,
                                         created=int(self.created.timestamp()))
