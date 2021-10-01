from uuid import UUID

import grpc
from fastapi import APIRouter, Depends, HTTPException

from courses.proto import courses_pb2_grpc, courses_pb2
from gateway.dependencies.courses import courses_stub
from gateway.dependencies.page_flags import PageFlags
from gateway.dependencies.sessions import sessions_stub
from gateway.dependencies.user import authorized_user_data
from gateway.schemas.course import Course, CourseCreate
from gateway.schemas.page import Page
from gateway.schemas.user import User
from sessions.proto import sessions_pb2_grpc, user_pb2

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/{id}", response_model=Course)
async def get_course_by_id(id: UUID, courses: courses_pb2_grpc.CoursesStub = Depends(courses_stub),
                           sessions: sessions_pb2_grpc.SessionsStub = Depends(sessions_stub)):
    try:
        course = await courses.FindCourseById(courses_pb2.CourseFindByIdRequest(id=str(id)))
        author = await sessions.FindUserById(user_pb2.UserFindByIdRequest(id=course.author_id))
        return Course(id=UUID(course.id),
                      name=course.name,
                      description=course.description if course.description else None,
                      author=author)
    except grpc.RpcError as e:
        if grpc.StatusCode.NOT_FOUND == e.code():
            raise HTTPException(status_code=404, detail="Not found")
        else:
            raise HTTPException(status_code=500)


@router.get("/", response_model=Page[Course])
async def get_courses(courses: courses_pb2_grpc.CoursesStub = Depends(courses_stub),
                      sessions: sessions_pb2_grpc.SessionsStub = Depends(sessions_stub),
                      user=Depends(authorized_user_data),
                      page_flags: PageFlags = Depends()):
    try:
        response = await courses.FindCourses(courses_pb2.CourseFindRequest(user_id=user["uid"],
                                                                           limit=page_flags.limit,
                                                                           offset=page_flags.offset))
        courses = []
        for result in response.results:
            author = await sessions.FindUserById(user_pb2.UserFindByIdRequest(id=result.author_id))
            courses.append(Course(id=UUID(result.id),
                                  name=result.name,
                                  description=result.description if result.description else None,
                                  author=author))
        return Page(results=courses, total_count=response.total_count, offset=page_flags.offset)
    except grpc.RpcError:
        raise HTTPException(status_code=500)


@router.post("/", response_model=Course, status_code=201)
async def create_course(course_create: CourseCreate,
                        courses: courses_pb2_grpc.CoursesStub = Depends(courses_stub),
                        sessions: sessions_pb2_grpc.SessionsStub = Depends(sessions_stub),
                        user=Depends(authorized_user_data)):
    try:
        course = await courses.CreateCourse(courses_pb2.CourseCreateRequest(name=course_create.name,
                                                                            description=course_create.description,
                                                                            author_id=user["uid"]))
        author = await sessions.FindUserById(user_pb2.UserFindByIdRequest(id=course.author_id))
        return Course(id=UUID(course.id),
                      name=course.name,
                      description=course.description,
                      author=author)
    except grpc.RpcError:
        raise HTTPException(status_code=500)


@router.get("/{id}/access", response_model=Page[User])
async def get_access(id: UUID, page_flags: PageFlags = Depends()):
    return Page(results=[], total_count=0, offset=0)


@router.put("/{id}/access/{uid}", status_code=204)
async def allow_access(id: UUID, uid: UUID):
    pass


@router.delete("/{id}/access/{uid}", status_code=204)
async def disallow_access(id: UUID, uid: UUID):
    pass
