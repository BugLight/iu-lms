from typing import Optional
from uuid import UUID

import grpclib.client
from fastapi import Depends

from courses.proto import courses_grpc, courses_pb2
from gateway.dependencies.sessions import SessionsContext
from gateway.schemas.course import Course, CourseCreate
from gateway.schemas.page import Page
from gateway.schemas.user import User
from gateway.settings import Settings, get_settings


async def courses_stub(settings: Settings = Depends(get_settings)) -> courses_grpc.CoursesStub:
    async with grpclib.client.Channel(settings.COURSES_HOST, settings.COURSES_PORT) as channel:
        yield courses_grpc.CoursesStub(channel)


class CoursesContext(object):
    def __init__(self, stub: courses_grpc.CoursesStub = Depends(courses_stub),
                 sessions: SessionsContext = Depends()):
        self._stub = stub
        self._sessions = sessions

    async def course_from_protobuf(self, pb: courses_pb2.CourseResponse) -> Course:
        author = await self._sessions.find_user_by_id(pb.author_id)
        return Course(id=pb.id,
                      name=pb.name,
                      description=pb.description if pb.description else None,
                      author=author)

    async def find_course_by_id(self, id: UUID) -> Optional[Course]:
        try:
            response = await self._stub.FindCourseById(courses_pb2.CourseFindByIdRequest(id=str(id)))
            return await self.course_from_protobuf(response)
        except grpclib.GRPCError as e:
            if e.status == grpclib.Status.NOT_FOUND:
                return None
            else:
                raise

    async def find_courses(self, user_id: Optional[UUID] = None,
                           name: Optional[str] = None,
                           author_id: Optional[UUID] = None,
                           limit: int = 10, offset: int = 0) -> Page[Course]:
        request = courses_pb2.CourseFindRequest(limit=limit, offset=offset)
        if user_id:
            request.user_id = str(user_id)
        if name:
            request.name = name
        if author_id:
            request.author_id = str(author_id)
        response = await self._stub.FindCourses(request)
        return Page(results=[await self.course_from_protobuf(result) for result in response.results],
                    total_count=response.total_count,
                    offset=offset)

    async def create_course(self, course_create: CourseCreate, author_id: UUID) -> Course:
        request = courses_pb2.CourseCreateRequest(author_id=str(author_id), name=course_create.name)
        if course_create.description:
            request.description = course_create.description
        response = await self._stub.CreateCourse(request)
        return await self.course_from_protobuf(response)

    async def get_access(self, id: UUID, limit: int = 10, offset: int = 0) -> Page[User]:
        response = await self._stub.GetCourseAccess(courses_pb2.CourseAccessRequest(course_id=str(id),
                                                                                    limit=limit,
                                                                                    offset=offset))
        users = [await self._sessions.find_user_by_id(result.user_id) for result in response.results]
        return Page(results=[user for user in users if user],
                    total_count=response.total_count,
                    offset=offset)

    async def modify_access(self, course_id: UUID, user_id: UUID, access: bool):
        await self._stub.ModifyAccess(courses_pb2.AccessRequest(course_id=str(course_id),
                                                                user_id=str(user_id),
                                                                access=access))
