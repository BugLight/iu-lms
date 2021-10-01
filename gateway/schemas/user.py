from datetime import date
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

import sessions.proto.user_pb2 as user_pb2


class RoleEnum(str, Enum):
    admin = "admin"
    student = "student"
    teacher = "teacher"


class UserBase(BaseModel):
    name: str
    email: EmailStr
    birth_date: Optional[date] = None
    role: RoleEnum


class User(UserBase):
    id: UUID

    @staticmethod
    def from_protobuf(pb: user_pb2.UserResponse):
        return User(id=UUID(pb.id),
                    name=pb.name,
                    email=pb.email,
                    role=pb.role,
                    birth_date=pb.birth_date if pb.birth_date else None)


class UserCreate(UserBase):
    def to_protobuf(self) -> user_pb2.UserCreateRequest:
        return user_pb2.UserCreateRequest(name=self.name,
                                          email=self.email,
                                          role=self.role,
                                          birth_date=self.birth_date if self.birth_date else None)
