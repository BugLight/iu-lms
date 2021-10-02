import logging
from typing import Optional
from uuid import UUID

import grpc
from fastapi import APIRouter, Depends, Body, HTTPException

from gateway.dependencies.auth import authorized
from sessions.proto import auth_pb2, user_pb2
from sessions.proto.sessions_pb2_grpc import SessionsStub

from gateway.dependencies.page_flags import PageFlags
from gateway.dependencies.sessions import sessions_stub
from gateway.schemas.page import Page
from gateway.schemas.user import User, UserCreate, RoleEnum

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=Page[User], dependencies=[Depends(authorized)])
async def get_users(role: Optional[RoleEnum] = None, name: Optional[str] = None, page_flags: PageFlags = Depends(),
                    sessions: SessionsStub = Depends(sessions_stub)):
    try:
        response = await sessions.FindUsers(user_pb2.UserFindRequest(name=name, role=role, limit=page_flags.limit,
                                                                     offset=page_flags.offset))
        return Page(results=[User.from_protobuf(result) for result in response.results],
                    total_count=response.total_count, offset=page_flags.offset)
    except grpc.RpcError as e:
        logging.error(e)
        raise HTTPException(status_code=500)


@router.get("/{id}", response_model=User, dependencies=[Depends(authorized)])
async def get_user_by_id(id: UUID, sessions: SessionsStub = Depends(sessions_stub)):
    try:
        user = await sessions.FindUserById(user_pb2.UserFindByIdRequest(id=str(id)))
        return User.from_protobuf(user)
    except grpc.RpcError as e:
        if grpc.StatusCode.NOT_FOUND == e.code():
            raise HTTPException(status_code=404, detail="User not found")
        else:
            logging.error(e)
            raise HTTPException(status_code=500)


@router.post("/", response_model=User, status_code=201)
async def create_user(user_create: UserCreate, sessions: SessionsStub = Depends(sessions_stub),
                      creator=Depends(authorized)):
    try:
        if creator["role"] != RoleEnum.admin:
            raise HTTPException(status_code=403)
        user = await sessions.CreateUser(user_create.to_protobuf())
        return User.from_protobuf(user)
    except grpc.RpcError as e:
        logging.error(e)
        raise HTTPException(status_code=500)


@router.post("/auth")
async def auth(login: str = Body(...), password: str = Body(...), sessions: SessionsStub = Depends(sessions_stub)):
    try:
        response = await sessions.Auth(auth_pb2.AuthRequest(login=login, password=password))
        return {"token": response.token}
    except grpc.RpcError as e:
        if grpc.StatusCode.UNAUTHENTICATED == e.code():
            raise HTTPException(status_code=401, detail="Incorrect login or password")
        else:
            logging.error(e)
            raise HTTPException(status_code=500)
