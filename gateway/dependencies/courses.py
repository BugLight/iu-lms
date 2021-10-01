import grpc.aio
from fastapi import Depends

from courses.proto import courses_pb2_grpc
from gateway.settings import Settings, get_settings


async def courses_stub(settings: Settings = Depends(get_settings)) -> courses_pb2_grpc.CoursesStub:
    async with grpc.aio.insecure_channel(settings.COURSES_HOST) as channel:
        yield courses_pb2_grpc.CoursesStub(channel)
