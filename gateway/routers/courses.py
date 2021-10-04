import logging
from typing import Optional
from uuid import UUID

import grpclib
from fastapi import APIRouter, Depends, HTTPException

from gateway.dependencies.auth import authorized
from gateway.dependencies.courses import CoursesContext
from gateway.dependencies.page_flags import PageFlags
from gateway.dependencies.sessions import SessionsContext
from gateway.schemas.course import Course, CourseCreate
from gateway.schemas.page import Page
from gateway.schemas.user import User, RoleEnum

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/{id}", response_model=Course, dependencies=[Depends(authorized)])
async def get_course_by_id(id: UUID, courses: CoursesContext = Depends()):
    try:
        course = await courses.find_course_by_id(id)
        if not course:
            raise HTTPException(status_code=404)
        return course
    except grpclib.GRPCError as e:
        logging.error(e)
        raise HTTPException(status_code=500)


@router.get("/", response_model=Page[Course])
async def get_courses(name: Optional[str] = None, author_id: Optional[str] = None,
                      courses: CoursesContext = Depends(),
                      user=Depends(authorized),
                      page_flags: PageFlags = Depends()):
    try:
        if user["role"] == RoleEnum.admin:
            user_id = None
        else:
            user_id = user["uid"]
        return await courses.find_courses(user_id=user_id, name=name, author_id=author_id, limit=page_flags.limit,
                                          offset=page_flags.offset)
    except grpclib.GRPCError as e:
        logging.error(e)
        raise HTTPException(status_code=500)


@router.post("/", response_model=Course, status_code=201)
async def create_course(course_create: CourseCreate,
                        courses: CoursesContext = Depends(),
                        user=Depends(authorized)):
    try:
        if user["role"] != RoleEnum.admin and user["role"] != RoleEnum.teacher:
            raise HTTPException(status_code=403)
        return await courses.create_course(course_create, user["uid"])
    except grpclib.GRPCError as e:
        logging.error(e)
        raise HTTPException(status_code=500)


@router.get("/{id}/access", response_model=Page[User], dependencies=[Depends(authorized)])
async def get_access(id: UUID, page_flags: PageFlags = Depends(),
                     courses: CoursesContext = Depends()):
    try:
        course = courses.find_course_by_id(id)
        if not course:
            raise HTTPException(status_code=404)
        return await courses.get_access(id, limit=page_flags.limit, offset=page_flags.offset)
    except grpclib.GRPCError as e:
        logging.error(e)
        raise HTTPException(status_code=500)


@router.put("/{id}/access/{uid}", status_code=204)
async def allow_access(id: UUID, uid: UUID,
                       courses: CoursesContext = Depends(),
                       sessions: SessionsContext = Depends(),
                       current_user=Depends(authorized)):
    try:
        user = await sessions.find_user_by_id(uid)
        if not user:
            raise HTTPException(status_code=404, detail="No such user")
        course = await courses.find_course_by_id(id)
        if not course:
            raise HTTPException(status_code=404, detail="No such course")
        if str(course.author.id) != current_user["uid"]:
            raise HTTPException(status_code=403)
        await courses.modify_access(id, uid, True)
    except grpclib.GRPCError as e:
        logging.error(e)
        raise HTTPException(status_code=500)


@router.delete("/{id}/access/{uid}", status_code=204)
async def disallow_access(id: UUID, uid: UUID,
                          courses: CoursesContext = Depends(),
                          sessions: SessionsContext = Depends(),
                          current_user=Depends(authorized)):
    try:
        user = await sessions.find_user_by_id(uid)
        if not user:
            raise HTTPException(status_code=404, detail="No such user")
        course = await courses.find_course_by_id(id)
        if not course:
            raise HTTPException(status_code=404, detail="No such course")
        if str(course.author.id) != current_user["uid"]:
            raise HTTPException(status_code=403)
        await courses.modify_access(id, uid, False)
    except grpclib.GRPCError as e:
        logging.error(e)
        raise HTTPException(status_code=500)
