import uuid
from typing import Optional

from courses.proto import courses_pb2
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session

from courses.models import Base
from courses.models.course import Course


class Access(Base):
    __tablename__ = "accesses"

    user_id = Column(UUID(as_uuid=True), primary_key=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey(Course.id), primary_key=True)

    def to_protobuf(self) -> courses_pb2.AccessResponse:
        return courses_pb2.AccessResponse(user_id=str(self.user_id),
                                          course_id=str(self.course_id))


class AccessRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_all(self, course_id: Optional[uuid.UUID] = None, limit: int = 10, offset: int = 0):
        query = self._session.query(Access)
        if course_id:
            query = query.filter_by(course_id=course_id)
        return query.offset(offset).limit(limit).all(), query.order_by(None).count()
