import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from gateway.dependencies.page_flags import PageFlags
from gateway.schemas.assignment import Assignment, AssignmentStatusEnum, AssignmentExtended, HistoryRecord
from gateway.schemas.attempt import Attempt
from gateway.schemas.course import Course
from gateway.schemas.page import Page
from gateway.schemas.review import ReviewCreate, Review
from gateway.schemas.task import Task, TaskCreate
from gateway.schemas.user import User

router = APIRouter(prefix="/tasks", tags=["tasks"])
task_author = User(id=uuid.uuid4(),
                   name="Task Author",
                   email="task_author@iulms.ml",
                   role="teacher")
task = Task(id=uuid.uuid4(),
            name="Test task",
            description="Test task description",
            course=Course(id=uuid.uuid4(),
                          name="Test course",
                          author=User(id=uuid.uuid4(),
                                      name="Course Author",
                                      email="course_author@iulms.ml",
                                      role="teacher")),
            author=task_author)
assignment = AssignmentExtended(created=datetime.now(),
                                updated=datetime.now(),
                                status=AssignmentStatusEnum.CHANGES_REQUESTED,
                                task=task,
                                assignee=User(id=uuid.uuid4(),
                                              name="Task Assignee",
                                              email="assignee@iulms.ml",
                                              role="student"),
                                history=[
                                    HistoryRecord(type="REVIEW",
                                                  time=datetime.now(),
                                                  record=Review(id=uuid.uuid4(),
                                                                author=task_author,
                                                                approved=False,
                                                                comment="Didn't work",
                                                                created=datetime.now())),
                                    HistoryRecord(type="ATTEMPT",
                                                  time=datetime.now(),
                                                  record=Attempt(id=uuid.uuid4(),
                                                                 created=datetime.now(),
                                                                 filename="file.zip"))
                                ])


@router.get("/", response_model=Page[Task])
async def get_tasks(course_id: Optional[UUID] = None, page_flags: PageFlags = Depends()):
    return Page(results=[task], total_count=1, offset=0)


@router.get("/{id}", response_model=Task)
async def get_task_by_id(id: UUID):
    if id != task.id:
        raise HTTPException(status_code=404, detail="Not found")
    return task


@router.post("/", response_model=Task, status_code=201)
async def create_task(task_create: TaskCreate):
    return task


@router.get("/{id}/assignments", response_model=Page[Assignment])
async def get_task_assignments(id: UUID, page_flags: PageFlags = Depends()):
    return Page(results=[Assignment(**assignment.dict())], total_count=1, offset=0)


@router.get("/{id}/assignments/{uid}", response_model=AssignmentExtended)
async def get_task_assignment_by_uid(id: UUID, uid: UUID):
    if id == assignment.task.id and uid == assignment.assignee.id:
        return assignment
    raise HTTPException(status_code=404, detail="Not found")


@router.put("/{id}/assignments/{uid}", response_model=Assignment)
async def assign_task_to_user(id: UUID, uid: UUID):
    return Assignment(**assignment.dict())


@router.post("/{id}/assignments/{uid}/attempts", response_model=Attempt, status_code=201)
async def upload_attempt(id: UUID, uid: UUID, file: UploadFile = File(...)):
    return Attempt(id=uuid.uuid4(), created=datetime.now(), filename=file.filename)


@router.post("/{id}/assignments/{uid}/reviews", response_model=Review, status_code=201)
async def create_review(id: UUID, uid: UUID, review_create: ReviewCreate):
    return Review(id=uuid.uuid4(), created=datetime.now(), author=task_author, **review_create.dict())
