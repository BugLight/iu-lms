import enum
import uuid
from typing import Optional

from sqlalchemy import Column, String, Enum, Date, LargeBinary, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session

from sessions.models import Base
from sessions.proto import user_pb2


class RoleEnum(str, enum.Enum):
    admin = "admin"
    student = "student"
    teacher = "teacher"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    role = Column(Enum(RoleEnum), nullable=False)
    birth_date = Column(Date)
    password = Column(LargeBinary, nullable=False)

    def to_protobuf(self):
        return user_pb2.UserResponse(id=str(self.id),
                                     name=self.name,
                                     email=self.email,
                                     role=self.role,
                                     birth_date=self.birth_date.isoformat() if self.birth_date else None)


class UserRepository:
    def __init__(self, session: Session):
        self._session = session

    def find_by_email(self, email: str):
        return self._session.query(User).filter_by(email=email).first()

    def find_by_id(self, id: uuid.UUID):
        return self._session.query(User).get(id)

    def get_all(self, name: Optional[str] = None, role: Optional[RoleEnum] = None, limit: int = 10, offset: int = 0):
        query = self._session.query(User)
        if name:
            query = query.filter(func.lower(User.name).contains(name.lower()))
        if role:
            query = query.filter_by(role=role)
        return query.offset(offset).limit(limit).all(), query.order_by(None).count()
