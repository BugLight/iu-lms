from asyncio import Lock
from typing import Optional
from uuid import UUID

import grpclib.client
from cachetools import Cache
from fastapi import Depends

from gateway.dependencies.cache import grpc_cache, aio_cachedmethod, grpc_cache_lock
from gateway.schemas.page import Page
from gateway.schemas.user import UserCreate, User, RoleEnum
from gateway.settings import Settings, get_settings
from sessions.proto import sessions_grpc, auth_pb2, user_pb2


async def sessions_stub(settings: Settings = Depends(get_settings)) -> sessions_grpc.SessionsStub:
    async with grpclib.client.Channel(settings.SESSIONS_HOST, settings.SESSIONS_PORT) as channel:
        yield sessions_grpc.SessionsStub(channel)


def user_from_protobuf(pb: user_pb2.UserResponse) -> User:
    return User(id=pb.id,
                name=pb.name,
                email=pb.email,
                role=pb.role,
                birth_date=pb.birth_date if pb.birth_date else None)


class SessionsContext(object):
    def __init__(self, stub: sessions_grpc.SessionsStub = Depends(sessions_stub),
                 cache: Cache = Depends(grpc_cache), lock: Lock = Depends(grpc_cache_lock)):
        self._stub = stub
        self._cache = cache
        self._lock = lock

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

    @aio_cachedmethod(lambda self: self._cache, lambda self: self._lock)
    async def find_user_by_id(self, id: UUID) -> Optional[User]:
        try:
            response = await self._stub.FindUserById(user_pb2.UserFindByIdRequest(id=str(id)))
            return user_from_protobuf(response)
        except grpclib.GRPCError as e:
            if e.status == grpclib.Status.NOT_FOUND:
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
