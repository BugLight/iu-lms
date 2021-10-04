import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

import grpclib.client
from fastapi import Depends, UploadFile

from gateway.dependencies.courses import CoursesContext
from gateway.dependencies.s3 import s3_client
from gateway.dependencies.sessions import SessionsContext
from gateway.schemas.assignment import Assignment, AssignmentExtended, HistoryRecord, HistoryRecordTypeEnum
from gateway.schemas.attempt import Attempt
from gateway.schemas.page import Page
from gateway.schemas.review import Review, ReviewCreate
from gateway.schemas.task import Task, TaskCreate
from gateway.settings import Settings, get_settings
from tasks.proto import assignment_pb2, attempt_pb2, review_pb2, tasks_grpc, task_pb2


async def tasks_stub(settings: Settings = Depends(get_settings)) -> tasks_grpc.TasksStub:
    async with grpclib.client.Channel(settings.TASKS_HOST, settings.TASKS_PORT) as channel:
        yield tasks_grpc.TasksStub(channel)


class TasksContext(object):
    def __init__(self, stub: tasks_grpc.TasksStub = Depends(tasks_stub),
                 sessions: SessionsContext = Depends(),
                 courses: CoursesContext = Depends(),
                 s3=Depends(s3_client)):
        self._stub = stub
        self._sessions = sessions
        self._courses = courses
        self._s3 = s3

    def attempt_from_protobuf(self, pb: attempt_pb2.AttemptResponse) -> Attempt:
        response = self._s3.head_object(Bucket="iu-lms", Key=pb.id)
        return Attempt(id=pb.id,
                       created=datetime.fromtimestamp(pb.created),
                       download_url=f"https://iu-lms.storage.yandexcloud.net/{pb.id}",
                       filename=response["Metadata"]["Filename"] if "Filename" in response["Metadata"] else None)

    async def task_from_protobuf(self, pb: task_pb2.TaskResponse) -> Task:
        author = await self._sessions.find_user_by_id(pb.author_id)
        course = await self._courses.find_course_by_id(pb.course_id)
        return Task(id=pb.id,
                    name=pb.name,
                    description=pb.description if pb.description else None,
                    author=author,
                    course=course)

    async def assignment_from_protobuf(self, pb: assignment_pb2.AssignmentResponse) -> Assignment:
        assignee = await self._sessions.find_user_by_id(pb.assignee_id)
        return Assignment(created=datetime.fromtimestamp(pb.created),
                          updated=datetime.fromtimestamp(pb.updated),
                          status=pb.status,
                          score=pb.score,
                          assignee=assignee)

    async def review_from_protobuf(self, pb: review_pb2.ReviewResponse) -> Review:
        author = await self._sessions.find_user_by_id(pb.author_id)
        return Review(id=pb.id,
                      created=datetime.fromtimestamp(pb.created),
                      approved=pb.approved,
                      comment=pb.comment if pb.comment else None,
                      score=pb.score if pb.score else None,
                      author=author)

    async def assignment_extended_from_protobuf(self, pb: assignment_pb2.AssignmentResponse) -> AssignmentExtended:
        assignment = await self.assignment_from_protobuf(pb)
        task = await self.find_task_by_id(pb.task_id)
        reviews = await self.find_reviews(pb.task_id, pb.assignee_id)
        attempts = await self.find_attempts(pb.task_id, pb.assignee_id)
        history = []
        for review in reviews.results:
            history.append(HistoryRecord(type=HistoryRecordTypeEnum.REVIEW,
                                         time=review.created,
                                         record=review))
        for attempt in attempts.results:
            history.append((HistoryRecord(type=HistoryRecordTypeEnum.ATTEMPT,
                                          time=attempt.created,
                                          record=attempt)))
        history.sort(key=lambda record: record.time)
        return AssignmentExtended(history=history,
                                  task=task,
                                  **assignment.dict())

    async def find_task_by_id(self, id: UUID) -> Optional[Task]:
        try:
            response = await self._stub.FindTaskById(task_pb2.TaskFindByIdRequest(id=str(id)))
            return await self.task_from_protobuf(response)
        except grpclib.GRPCError as e:
            if e.status == grpclib.Status.NOT_FOUND:
                return None
            else:
                raise

    async def find_tasks(self, user_id: Optional[UUID] = None,
                         course_id: Optional[UUID] = None,
                         limit: int = 10, offset: int = 0) -> Page[Task]:
        request = task_pb2.TaskFindRequest(limit=limit, offset=offset)
        if user_id:
            request.user_id = str(user_id)
        if course_id:
            request.course_id = str(course_id)
        response = await self._stub.FindTasks(request)
        return Page(results=[await self.task_from_protobuf(result) for result in response.results],
                    total_count=response.total_count,
                    offset=offset)

    async def create_task(self, task_create: TaskCreate, author_id: UUID) -> Task:
        request = task_pb2.TaskCreateRequest(name=task_create.name,
                                             course_id=str(task_create.course_id),
                                             author_id=str(author_id))
        if task_create.description:
            request.description = task_create.description
        response = await self._stub.CreateTask(request)
        return await self.task_from_protobuf(response)

    async def find_assignments(self, task_id: UUID, limit: int = 10, offset: int = 0) -> Page[Assignment]:
        response = await self._stub.FindAssignments(assignment_pb2.AssignmentFindRequest(task_id=str(task_id),
                                                                                         limit=limit, offset=offset))
        return Page(results=[await self.assignment_from_protobuf(result) for result in response.results],
                    total_count=response.total_count,
                    offset=offset)

    async def find_assignment_by_id(self, task_id: UUID, assignee_id: UUID) -> Optional[AssignmentExtended]:
        try:
            response = await self._stub.FindAssignmentById(assignment_pb2.AssignmentFindByIdRequest(
                task_id=str(task_id),
                assignee_id=str(assignee_id)))
            return await self.assignment_extended_from_protobuf(response)
        except grpclib.GRPCError as e:
            if e.status == grpclib.Status.NOT_FOUND:
                return None
            else:
                raise

    async def create_assignment(self, task_id: UUID, assignee_id: UUID) -> Assignment:
        response = await self._stub.CreateAssignment(assignment_pb2.AssignmentCreateRequest(
            task_id=str(task_id),
            assignee_id=str(assignee_id)))
        return await self.assignment_from_protobuf(response)

    async def create_review(self, task_id: UUID, assignee_id: UUID, review_create: ReviewCreate,
                            author_id: UUID) -> Review:
        request = review_pb2.ReviewCreateRequest(task_id=str(task_id),
                                                 assignee_id=str(assignee_id),
                                                 author_id=str(author_id),
                                                 approved=review_create.approved)
        if review_create.comment:
            request.comment = review_create.comment
        if review_create.score:
            request.score = review_create.score
        response = await self._stub.CreateReview(request)
        return await self.review_from_protobuf(response)

    async def create_attempt(self, task_id: UUID, assignee_id: UUID, file: UploadFile) -> Attempt:
        id = uuid.uuid4()
        self._s3.put_object(Bucket="iu-lms",
                            Key=str(id),
                            Body=file.file,
                            ACL="public-read",
                            Metadata={"Filename": file.filename})
        response = await self._stub.CreateAttempt(attempt_pb2.AttemptCreateRequest(id=str(id),
                                                                                   task_id=str(task_id),
                                                                                   assignee_id=str(assignee_id)))
        return self.attempt_from_protobuf(response)

    async def find_reviews(self, task_id: UUID, assignee_id: UUID, limit: int = 10, offset: int = 0) -> Page[Review]:
        response = await self._stub.FindReviews(review_pb2.ReviewFindRequest(task_id=str(task_id),
                                                                             assignee_id=str(assignee_id),
                                                                             limit=limit,
                                                                             offset=offset))
        return Page(results=[await self.review_from_protobuf(result) for result in response.results],
                    total_count=response.total_count,
                    offset=offset)

    async def find_attempts(self, task_id: UUID, assignee_id: UUID, limit: int = 10, offset: int = 0) -> Page[Attempt]:
        response = await self._stub.FindAttempts(attempt_pb2.AttemptFindRequest(task_id=str(task_id),
                                                                                assignee_id=str(assignee_id),
                                                                                limit=limit,
                                                                                offset=offset))
        return Page(results=[self.attempt_from_protobuf(result) for result in response.results],
                    total_count=response.total_count,
                    offset=offset)
