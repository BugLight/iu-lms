import logging

import grpc
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from gateway.dependencies.sessions import sessions_stub
from sessions.proto import sessions_pb2_grpc, auth_pb2

bearer = HTTPBearer()


async def authorized(credentials: HTTPAuthorizationCredentials = Depends(bearer),
                     sessions: sessions_pb2_grpc.SessionsStub = Depends(sessions_stub)):
    try:
        validation_result = await sessions.Validate(auth_pb2.ValidateRequest(token=credentials.credentials))
        if not validation_result.valid:
            raise HTTPException(status_code=401)
        return jwt.decode(credentials.credentials, options={"verify_signature": False})
    except grpc.RpcError as e:
        logging.error(e)
        raise HTTPException(status_code=500)

