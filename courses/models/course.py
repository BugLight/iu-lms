import uuid
from typing import Optional

from courses.models.access import Access
from courses.proto import courses_pb2
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session

from courses.models import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)

    def to_protobuf(self) -> courses_pb2.CourseResponse:
        return courses_pb2.CourseResponse(id=str(self.id),
                                          author_id=str(self.author_id),
                                          name=self.name,
                                          description=self.description)


class CourseRepository:
    def __init__(self, session: Session):
        self._session = session

    def find_by_id(self, id: uuid.UUID):
        return self._session.query(Course).get(id)

    def get_all(self, user_id: Optional[uuid.UUID] = None,
                author_id: Optional[uuid.UUID] = None,
                name: Optional[str] = None,
                limit: int = 10, offset: int = 0):
        query = self._session.query(Course)
        if user_id:
            query = query.join(Access).filter_by(user_id=user_id)
        if author_id:
            query = query.filter_by(author_id=author_id)
        if name:
            query = query.filter(Course.name.lower().startswith(name.lower()))
        return query.offset(offset).limit(limit).all, query.order_by(None).count()
