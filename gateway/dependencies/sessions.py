from typing import Optional
from uuid import UUID

import grpc
from fastapi import Depends

from gateway.schemas.page import Page
from gateway.schemas.user import UserCreate, User, RoleEnum
from sessions.proto import sessions_pb2_grpc, auth_pb2, user_pb2

from gateway.settings import Settings, get_settings


async def sessions_stub(settings: Settings = Depends(get_settings)) -> sessions_pb2_grpc.SessionsStub:
    async with grpc.aio.insecure_channel(settings.SESSIONS_HOST) as channel:
        yield sessions_pb2_grpc.SessionsStub(channel)


def user_from_protobuf(pb: user_pb2.UserResponse) -> User:
    return User(id=pb.id,
                name=pb.name,
                email=pb.email,
                role=pb.role,
                birth_date=pb.birth_date if pb.birth_date else None)


class SessionsContext(object):
    def __init__(self, stub: sessions_pb2_grpc.SessionsStub = Depends(sessions_stub)):
        self._stub = stub

    async def authorize(self, login: str, password: str) -> dict:
        response = await self._stub.Auth(auth_pb2.AuthRequest(login=login, password=password))
        return {"token": response.token}

    async def create_user(self, user_create: UserCreate):
        request = user_pb2.UserCreateRequest(name=user_create.name,
                                             email=user_create.email,
                                             role=user_create.role)
        if user_create.birth_date:
            request.birth_date = user_create.birth_date.isoformat()
        response = await self._stub.CreateUser(request)
        return user_from_protobuf(response)

    async def find_user_by_id(self, id: UUID) -> Optional[User]:
        try:
            response = await self._stub.FindUserById(user_pb2.UserFindByIdRequest(id=str(id)))
            return user_from_protobuf(response)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            else:
                raise

    async def find_users(self, role: Optional[RoleEnum] = None, name: Optional[str] = None,
                         limit: int = 10, offset: int = 0) -> Page[User]:
        request = user_pb2.UserFindRequest(limit=limit, offset=offset)
        if role:
            request.role = role
        if name:
            request.name = name
        response = await self._stub.FindUsers(request)
        return Page(results=[user_from_protobuf(result) for result in response.results],
                    total_count=response.total_count,
                    offset=offset)

    async def validate(self, token: str) -> bool:
        response = await self._stub.Validate(auth_pb2.ValidateRequest(token=token))
        return response.valid
