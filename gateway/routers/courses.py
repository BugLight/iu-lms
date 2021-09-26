import uuid
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from gateway.dependencies.page_flags import PageFlags
from gateway.schemas.course import Course, CourseCreate
from gateway.schemas.page import Page
from gateway.schemas.user import User

router = APIRouter(prefix="/courses", tags=["courses"])
author = User(name="Admin",
              role="admin",
              id=UUID("d438a258-f8aa-477e-bb91-0d921b72ac70"),
              email="admin@iulms.ml",
              birth_date=datetime.fromisoformat("1999-05-21"))
courses = [
    Course(id=UUID("2c8a518e-240b-4faf-99f0-a7bbcf58b8e1"),
           name="Object oriented programming",
           author=author,
           description="""This Specialization is for aspiring software developers with some programming experience in 
at least one other programming language (e.g., Python, C, JavaScript, etc.) who want to be able to solve 
more complex problems through objected-oriented design with Java. In addition to learning Java, 
you will gain experience with two Java development environments (BlueJ and Eclipse), learn how to program 
with graphical user interfaces, and learn how to design programs capable of managing large amounts of 
data. These software engineering skills are broadly applicable across wide array of industries.""")
]


@router.get("/{id}", response_model=Course)
async def get_course_by_id(id: UUID):
    found = filter(lambda c: c.id == id, courses)
    for course in found:
        return course
    raise HTTPException(status_code=404, detail="Not found")


@router.get("/", response_model=Page[Course])
async def get_courses(page_flags: PageFlags = Depends()):
    return Page(results=courses[page_flags.offset:page_flags.offset + page_flags.limit],
                total_count=len(courses),
                offset=page_flags.offset)


@router.post("/", response_model=Course, status_code=201)
async def create_course(course_create: CourseCreate):
    course = Course(id=uuid.uuid4(), author=author, **course_create.dict())
    courses.append(course)
    return course


@router.delete("/{id}", status_code=204)
async def delete_course(id: UUID):
    for course in courses:
        if course.id == id:
            courses.remove(course)
            return


@router.get("/{id}/access", response_model=Page[User])
async def get_access(id: UUID, page_flags: PageFlags = Depends()):
    return Page(results=[], total_count=0, offset=0)


@router.put("/{id}/access/{uid}", status_code=204)
async def allow_access(id: UUID, uid: UUID):
    pass


@router.delete("/{id}/access/{uid}", status_code=204)
async def disallow_access(id: UUID, uid: UUID):
    pass
