import logging

import grpc
from sqlalchemy.exc import SQLAlchemyError

from courses.db import SessionLocal
from courses.models.course import Access, Course, CourseRepository
from courses.proto import courses_pb2
from courses.proto.courses_pb2_grpc import CoursesServicer


class CoursesService(CoursesServicer):
    def CreateCourse(self, request: courses_pb2.CourseCreateRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal.begin() as session:
                course = Course(name=request.name,
                                description=request.description if request.description else None,
                                author_id=request.author_id)
                session.add(course)
                session.flush()
                return course.to_protobuf()
        except SQLAlchemyError as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not create course")

    def FindCourseById(self, request: courses_pb2.CourseFindByIdRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal() as session:
                repository = CourseRepository(session)
                course = repository.find_by_id(request.id)
                if not course:
                    context.abort(grpc.StatusCode.NOT_FOUND, "No course with such id")
                return course.to_protobuf()
        except SQLAlchemyError as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not find course")

    def FindCourses(self, request: courses_pb2.CourseFindRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal() as session:
                repository = CourseRepository(session)
                courses, total_count = repository.get_all(user_id=request.user_id,
                                                          author_id=request.author_id,
                                                          name=request.name,
                                                          limit=request.limit, offset=request.offset)
                return courses_pb2.CourseFindResponse(results=[course.to_protobuf() for course in courses],
                                                      total_count=total_count)
        except SQLAlchemyError as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not find courses")

    def ModifyAccess(self, request: courses_pb2.AccessRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal.begin() as session:
                repository = CourseRepository(session)
                if request.access:
                    repository.grant_access(request.course_id, request.user_id)
                else:
                    repository.revoke_access(request.course_id, request.user_id)
                return courses_pb2.AccessResponse(user_id=request.user_id)
        except SQLAlchemyError as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not modify course access")

    def GetCourseAccess(self, request: courses_pb2.CourseAccessRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal() as session:
                repository = CourseRepository(session)
                accesses, total_count = repository.get_access(request.course_id,
                                                              limit=request.limit,
                                                              offset=request.offset)
                return courses_pb2.CourseAccessResponse(results=[access.to_protobuf() for access in accesses],
                                                        total_count=total_count)
        except SQLAlchemyError as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not get course accesses")
