import logging
import uuid
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from smtplib import SMTPException

import grpc
import jwt
from sessions.proto.auth_pb2 import AuthResponse, AuthRequest, ValidateRequest, ValidateResponse
from sessions.proto.sessions_pb2_grpc import SessionsServicer
from sessions.proto.user_pb2 import UserFindRequest, UserFindByIdRequest, UserCreateRequest, UserResponse, \
    UserFindResponse
from sqlalchemy.exc import SQLAlchemyError

from sessions.db import SessionLocal
from sessions.mail import smtp_client
from sessions.models.user import User, UserRepository
from sessions.password import generate_password, hash_password
from sessions.settings import settings


class SessionsService(SessionsServicer):
    def Auth(self, request: AuthRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal() as session:
                repository = UserRepository(session)
                user = repository.find_by_email(request.login)
                if not user or hash_password(request.password) != user.password:
                    context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid login or password")
                token = jwt.encode({
                    "uid": str(user.id),
                    "name": user.name,
                    "role": user.role,
                    "iat": datetime.utcnow(),
                    "exp": datetime.utcnow() + timedelta(seconds=settings.JWT_LIFETIME)
                }, settings.JWT_SECRET)
                return AuthResponse(token=token)
        except SQLAlchemyError as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not authorize user")

    def CreateUser(self, request: UserCreateRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal() as session:
                repository = UserRepository(session)
                if repository.find_by_email(request.email):
                    context.abort(grpc.StatusCode.ALREADY_EXISTS, "Email is already in use")
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
                session.commit()
                return user.to_protobuf()
        except SMTPException as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not send password email")
        except SQLAlchemyError as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not create user")

    def FindUsers(self, request: UserFindRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal() as session:
                repository = UserRepository(session)
                users, total_count = repository.get_all(name=request.name, role=request.role,
                                                        limit=request.limit, offset=request.offset)
                return UserFindResponse(results=[user.to_protobuf() for user in users], total_count=total_count)
        except SQLAlchemyError:
            context.abort(grpc.StatusCode.ABORTED, "Could not find users")

    def FindUserById(self, request: UserFindByIdRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal() as session:
                repository = UserRepository(session)
                user = repository.find_by_id(request.id)
                if not user:
                    context.abort(grpc.StatusCode.NOT_FOUND, "No user with such id")
                return user.to_protobuf()
        except SQLAlchemyError as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not find user")

    def Validate(self, request: ValidateRequest, context: grpc.ServicerContext):
        try:
            jwt.decode(request.token, settings.JWT_SECRET, algorithms=["HS256"])
            return ValidateResponse(valid=True)
        except jwt.InvalidTokenError:
            return ValidateResponse(valid=False)
