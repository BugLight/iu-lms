import logging
import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

import grpclib
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from gateway.dependencies.auth import authorized
from gateway.dependencies.page_flags import PageFlags
from gateway.dependencies.tasks import TasksContext
from gateway.schemas.assignment import Assignment, AssignmentExtended
from gateway.schemas.attempt import Attempt
from gateway.schemas.page import Page
from gateway.schemas.review import ReviewCreate, Review
from gateway.schemas.task import Task, TaskCreate
from gateway.schemas.user import RoleEnum

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=Page[Task])
async def get_tasks(course_id: Optional[UUID] = None,
                    tasks: TasksContext = Depends(),
                    user=Depends(authorized),
                    page_flags: PageFlags = Depends()):
    try:
        if user["role"] == RoleEnum.admin:
            user_id = None
        else:
            user_id = user["uid"]
        return await tasks.find_tasks(user_id=user_id, course_id=course_id,
                                      limit=page_flags.limit, offset=page_flags.offset)
    except grpclib.GRPCError as e:
        logging.error(e)
        raise HTTPException(status_code=500)


@router.get("/{id}", response_model=Task, dependencies=[Depends(authorized)])
async def get_task_by_id(id: UUID, tasks: TasksContext = Depends()):
    try:
        task = await tasks.find_task_by_id(id)
        if not task:
            raise HTTPException(status_code=404)
        return task
    except grpclib.GRPCError as e:
        logging.error(e)
        raise HTTPException(status_code=500)


@router.post("/", response_model=Task, status_code=201)
async def create_task(task_create: TaskCreate,
                      tasks: TasksContext = Depends(),
                      user=Depends(authorized)):
    try:
        if user["role"] != RoleEnum.admin and user["role"] != RoleEnum.teacher:
            raise HTTPException(status_code=403)
        return await tasks.create_task(task_create, user["uid"])
    except grpclib.GRPCError as e:
        logging.error(e)
        raise HTTPException(status_code=500)


@router.get("/{id}/assignments", response_model=Page[Assignment])
async def get_task_assignments(id: UUID, page_flags: PageFlags = Depends(),
                               tasks: TasksContext = Depends(),
                               user=Depends(authorized)):
    try:
        task = await tasks.find_task_by_id(id)
        if not task:
            raise HTTPException(status_code=404)
        return await tasks.find_assignments(id, limit=page_flags.limit, offset=page_flags.offset)
    except grpclib.GRPCError as e:
        logging.error(e)
        raise HTTPException(status_code=500)


@router.get("/{id}/assignments/{uid}", response_model=AssignmentExtended, dependencies=[Depends(authorized)])
async def get_task_assignment_by_uid(id: UUID, uid: UUID,
                                     tasks: TasksContext = Depends()):
    try:
        task = await tasks.find_task_by_id(id)
        if not task:
            raise HTTPException(status_code=404)
        assignment = await tasks.find_assignment_by_id(id, uid)
        if not assignment:
            raise HTTPException(status_code=404)
        return assignment
    except grpclib.GRPCError as e:
        logging.error(e)
        raise HTTPException(status_code=500)


@router.put("/{id}/assignments/{uid}", response_model=Assignment)
async def assign_task_to_user(id: UUID, uid: UUID,
                              tasks: TasksContext = Depends(),
                              user=Depends(authorized)):
    try:
        task = await tasks.find_task_by_id(id)
        if not task:
            raise HTTPException(status_code=404)
        if user["role"] != RoleEnum.admin and user["role"] != RoleEnum.teacher:
            raise HTTPException(status_code=403)
        assignment = await tasks.find_assignment_by_id(id, uid)
        if assignment:
            return assignment
        return await tasks.create_assignment(id, uid)
    except grpclib.GRPCError as e:
        logging.error(e)
        raise HTTPException(status_code=500)


@router.post("/{id}/assignments/{uid}/attempts", response_model=Attempt, status_code=201)
async def upload_attempt(id: UUID, uid: UUID, file: UploadFile = File(...)):
    return Attempt(id=uuid.uuid4(), created=datetime.now(), filename=file.filename)


@router.post("/{id}/assignments/{uid}/reviews", response_model=Review, status_code=201)
async def create_review(id: UUID, uid: UUID, review_create: ReviewCreate,
                        tasks: TasksContext = Depends(),
                        user=Depends(authorized)):
    try:
        task = await tasks.find_task_by_id(id)
        if not task:
            raise HTTPException(status_code=404)
        if user["role"] != RoleEnum.admin and user["role"] != RoleEnum.teacher:
            raise HTTPException(status_code=403)
        return await tasks.create_review(id, uid, review_create, author_id=user["uid"])
    except grpclib.GRPCError as e:
        logging.error(e)
        raise HTTPException(status_code=500)

