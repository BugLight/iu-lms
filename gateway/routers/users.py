import logging
from typing import Optional
from uuid import UUID

import grpclib
from fastapi import APIRouter, Depends, Body, HTTPException

from gateway.dependencies.auth import authorized
from gateway.dependencies.page_flags import PageFlags
from gateway.dependencies.sessions import SessionsContext
from gateway.schemas.page import Page
from gateway.schemas.user import User, UserCreate, RoleEnum

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=Page[User], dependencies=[Depends(authorized)])
async def get_users(role: Optional[RoleEnum] = None, name: Optional[str] = None, page_flags: PageFlags = Depends(),
                    sessions: SessionsContext = Depends()):
    try:
        return await sessions.find_users(role=role, name=name, limit=page_flags.limit, offset=page_flags.offset)
    except grpclib.GRPCError as e:
        logging.error(e)
        raise HTTPException(status_code=500)


@router.get("/{id}", response_model=User, dependencies=[Depends(authorized)])
async def get_user_by_id(id: UUID, sessions: SessionsContext = Depends()):
    try:
        user = await sessions.find_user_by_id(id)
        if not user:
            raise HTTPException(status_code=404)
        return user
    except grpclib.GRPCError as e:
        logging.error(e)
        raise HTTPException(status_code=500)


@router.post("", response_model=User, status_code=201)
async def create_user(user_create: UserCreate,
                      sessions: SessionsContext = Depends(),
                      creator=Depends(authorized)):
    try:
        if creator["role"] != RoleEnum.admin:
            raise HTTPException(status_code=403)
        return await sessions.create_user(user_create)
    except grpclib.GRPCError as e:
        logging.error(e)
        raise HTTPException(status_code=500)


@router.post("/auth")
async def auth(login: str = Body(...), password: str = Body(...),
               sessions: SessionsContext = Depends()):
    try:
        return await sessions.authorize(login, password)
    except grpclib.GRPCError as e:
        if e.status == grpclib.Status.UNAUTHENTICATED:
            raise HTTPException(status_code=401, detail="Incorrect login or password")
        else:
            logging.error(e)
            raise HTTPException(status_code=500)
