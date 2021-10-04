import logging

import grpclib
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from gateway.dependencies.sessions import SessionsContext

bearer = HTTPBearer()


async def authorized(credentials: HTTPAuthorizationCredentials = Depends(bearer),
                     sessions: SessionsContext = Depends()):
    try:
        if not await sessions.validate(credentials.credentials):
            raise HTTPException(status_code=401)
        return jwt.decode(credentials.credentials, options={"verify_signature": False})
    except grpclib.GRPCError as e:
        logging.error(e)
        raise HTTPException(status_code=500)

