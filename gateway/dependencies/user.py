from typing import Optional

import grpc
import jwt
from fastapi import Header, HTTPException, Depends

from gateway.dependencies.sessions import sessions_stub
from sessions.proto import sessions_pb2_grpc, auth_pb2


async def authorized_user_data(authorization: Optional[str] = Header(None),
                               sessions: sessions_pb2_grpc.SessionsStub = Depends(sessions_stub)):
    if not authorization:
        raise HTTPException(status_code=401)
    scheme, payload = authorization.split(" ")
    if scheme != "Bearer":
        raise HTTPException(status_code=401)
    try:
        validation_result = await sessions.Validate(auth_pb2.ValidateRequest(token=payload))
        if not validation_result.valid:
            raise HTTPException(status_code=401)
        return jwt.decode(payload, options={"verify_signature": False})
    except grpc.RpcError:
        raise HTTPException(status_code=500)

