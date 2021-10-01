import grpc
from fastapi import Depends

from sessions.proto.sessions_pb2_grpc import SessionsStub

from gateway.settings import Settings, get_settings


async def sessions_stub(settings: Settings = Depends(get_settings)):
    async with grpc.aio.insecure_channel(settings.SESSIONS_HOST) as channel:
        yield SessionsStub(channel)
