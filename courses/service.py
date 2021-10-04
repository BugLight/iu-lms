import logging

import grpclib.server
from sqlalchemy.exc import SQLAlchemyError

from courses.db import SessionLocal
from courses.models.course import Course, CourseRepository
from courses.proto import courses_pb2, courses_grpc


class CoursesService(courses_grpc.CoursesBase):
    async def CreateCourse(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal.begin() as session:
                course = Course(name=request.name,
                                description=request.description if request.description else None,
                                author_id=request.author_id)
                session.add(course)
                session.flush()
                await stream.send_message(course.to_protobuf())
        except SQLAlchemyError as e:
            logging.error(e)
            raise grpclib.GRPCError(status=grpclib.Status.ABORTED, message="Could not create course")

    async def FindCourseById(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal() as session:
                repository = CourseRepository(session)
                course = repository.find_by_id(request.id)
                if not course:
                    raise grpclib.GRPCError(status=grpclib.Status.NOT_FOUND, message="No course with such id")
                await stream.send_message(course.to_protobuf())
        except SQLAlchemyError as e:
            logging.error(e)
            raise grpclib.GRPCError(status=grpclib.Status.ABORTED, message="Could not find course")

    async def FindCourses(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal() as session:
                repository = CourseRepository(session)
                courses, total_count = repository.get_all(user_id=request.user_id,
                                                          author_id=request.author_id,
                                                          name=request.name,
                                                          limit=request.limit, offset=request.offset)
                await stream.send_message(courses_pb2.CourseFindResponse(results=[course.to_protobuf()
                                                                                  for course in courses],
                                                                         total_count=total_count))
        except SQLAlchemyError as e:
            logging.error(e)
            raise grpclib.GRPCError(status=grpclib.Status.ABORTED, message="Could not find courses")

    async def ModifyAccess(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal.begin() as session:
                repository = CourseRepository(session)
                if request.access:
                    repository.grant_access(request.course_id, request.user_id)
                else:
                    repository.revoke_access(request.course_id, request.user_id)
                await stream.send_message(courses_pb2.AccessResponse(user_id=request.user_id))
        except SQLAlchemyError as e:
            logging.error(e)
            raise grpclib.GRPCError(status=grpclib.Status.ABORTED, message="Could not modify course access")

    async def GetCourseAccess(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal() as session:
                repository = CourseRepository(session)
                accesses, total_count = repository.get_access(request.course_id,
                                                              limit=request.limit,
                                                              offset=request.offset)
                await stream.send_message(courses_pb2.CourseAccessResponse(results=[access.to_protobuf()
                                                                                    for access in accesses],
                                                                           total_count=total_count))
        except SQLAlchemyError as e:
            logging.error(e)
            raise grpclib.GRPCError(status=grpclib.Status.ABORTED, message="Could not get course accesses")
