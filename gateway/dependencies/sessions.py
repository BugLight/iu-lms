import grpc

from sessions.proto.sessions_pb2_grpc import SessionsStub


async def sessions_stub():
    async with grpc.aio.insecure_channel("localhost:3000") as channel:
        yield SessionsStub(channel)
