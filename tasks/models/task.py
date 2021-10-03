import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from tasks.models import Base
from tasks.proto import task_pb2


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    author_id = Column(UUID(as_uuid=True), nullable=False)
    course_id = Column(UUID(as_uuid=True), nullable=False)

    def to_protobuf(self) -> task_pb2.TaskResponse:
        return task_pb2.TaskResponse(id=str(self.id),
                                     name=self.name,
                                     description=self.description,
                                     author_id=str(self.author_id),
                                     course_id=str(self.course_id))
