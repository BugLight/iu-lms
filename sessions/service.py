import logging
import uuid
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from smtplib import SMTPException

import grpclib.server
import jwt
from sessions.proto.auth_pb2 import AuthResponse, AuthRequest, ValidateRequest, ValidateResponse
from sessions.proto.sessions_grpc import SessionsBase
from sessions.proto.user_pb2 import UserFindRequest, UserFindByIdRequest, UserCreateRequest, UserResponse, \
    UserFindResponse
from sqlalchemy.exc import SQLAlchemyError

from sessions.db import SessionLocal
from sessions.mail import smtp_client
from sessions.models.user import User, UserRepository
from sessions.password import generate_password, hash_password
from sessions.settings import settings


class SessionsService(SessionsBase):
    async def Auth(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal() as session:
                repository = UserRepository(session)
                user = repository.find_by_email(request.login)
                if not user or hash_password(request.password) != user.password:
                    raise grpclib.GRPCError(status=grpclib.Status.UNAUTHENTICATED, message="Invalid login or password")
                token = jwt.encode({
                    "uid": str(user.id),
                    "name": user.name,
                    "role": user.role,
                    "iat": datetime.utcnow(),
                    "exp": datetime.utcnow() + timedelta(seconds=settings.JWT_LIFETIME)
                }, settings.JWT_SECRET)
                await stream.send_message(AuthResponse(token=token))
        except SQLAlchemyError as e:
            logging.error(e)
            raise grpclib.GRPCError(status=grpclib.Status.ABORTED, message="Could not authorize user")

    async def CreateUser(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal.begin() as session:
                repository = UserRepository(session)
                if repository.find_by_email(request.email):
                    raise grpclib.GRPCError(status=grpclib.Status.ALREADY_EXISTS, message="Email is already in use")
                password = generate_password()
                message = MIMEText("Your password is %s" % password)
                with smtp_client() as client:
                    client.send_message(message, from_addr=settings.SMTP_FROM, to_addrs=[request.email])
                user = User(name=request.name,
                            email=request.email,
                            role=request.role,
                            birth_date=request.birth_date if request.birth_date else None,
                            password=hash_password(password))
                session.add(user)
                session.flush()
                await stream.send_message(user.to_protobuf())
        except SMTPException as e:
            logging.error(e)
            raise grpclib.GRPCError(grpclib.Status.ABORTED, message="Could not send password email")
        except SQLAlchemyError as e:
            logging.error(e)
            raise grpclib.GRPCError(grpclib.Status.ABORTED, message="Could not create user")

    async def FindUsers(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal() as session:
                repository = UserRepository(session)
                users, total_count = repository.get_all(name=request.name, role=request.role,
                                                        limit=request.limit, offset=request.offset)
                await stream.send_message(UserFindResponse(results=[user.to_protobuf() for user in users],
                                                           total_count=total_count))
        except SQLAlchemyError:
            raise grpclib.GRPCError(status=grpclib.Status.ABORTED, message="Could not find users")

    async def FindUserById(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal() as session:
                repository = UserRepository(session)
                user = repository.find_by_id(request.id)
                if not user:
                    raise grpclib.GRPCError(status=grpclib.Status.NOT_FOUND, message="No user with such id")
                await stream.send_message(user.to_protobuf())
        except SQLAlchemyError as e:
            logging.error(e)
            raise grpclib.GRPCError(status=grpclib.Status.ABORTED, message="Could not find user")

    async def Validate(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            jwt.decode(request.token, settings.JWT_SECRET, algorithms=["HS256"])
            await stream.send_message(ValidateResponse(valid=True))
        except jwt.InvalidTokenError:
            await stream.send_message(ValidateResponse(valid=False))
