import logging

import grpclib.server
from sqlalchemy.exc import SQLAlchemyError
from tasks.proto.tasks_grpc import TasksBase

from tasks.db import SessionLocal
from tasks.models.assignment import Assignment, AssignmentStatusEnum
from tasks.models.attempt import Attempt
from tasks.models.review import Review
from tasks.models.task import Task
from tasks.proto import assignment_pb2, attempt_pb2, review_pb2, task_pb2
from tasks.repository.assignment import AssignmentRepository
from tasks.repository.task import TaskRepository


class TasksService(TasksBase):
    async def CreateTask(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal.begin() as session:
                task = Task(name=request.name,
                            description=request.description if request.description else None,
                            author_id=request.author_id,
                            course_id=request.course_id)
                session.add(task)
                session.flush()
                await stream.send_message(task.to_protobuf())
        except SQLAlchemyError as e:
            logging.error(e)
            raise grpclib.GRPCError(status=grpclib.Status.ABORTED, message="Could not create task")

    async def FindTaskById(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal() as session:
                repository = TaskRepository(session)
                task = repository.find_by_id(request.id)
                if not task:
                    raise grpclib.GRPCError(status=grpclib.Status.NOT_FOUND, message="No task with such id")
                await stream.send_message(task.to_protobuf())
        except SQLAlchemyError as e:
            logging.error(e)
            raise grpclib.GRPCError(status=grpclib.Status.ABORTED, message="Could not find task")

    async def FindTasks(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal() as session:
                repository = TaskRepository(session)
                tasks, total_count = repository.find_tasks(user_id=request.user_id, course_id=request.course_id,
                                                           limit=request.limit, offset=request.offset)
                await stream.send_message(task_pb2.TaskFindResponse(results=[task.to_protobuf() for task in tasks],
                                                                    total_count=total_count))
        except SQLAlchemyError as e:
            logging.error(e)
            raise grpclib.GRPCError(status=grpclib.Status.ABORTED, message="Could not find tasks")

    async def CreateAssignment(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal.begin() as session:
                assignment = Assignment(task_id=request.task_id, assignee_id=request.assignee_id)
                session.add(assignment)
                session.flush()
                await stream.send_message(assignment.to_protobuf())
        except SQLAlchemyError as e:
            logging.error(e)
            raise grpclib.GRPCError(status=grpclib.Status.ABORTED, message="Could not create assignment")

    async def UpdateAssignment(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal.begin() as session:
                repository = AssignmentRepository(session)
                assignment = repository.update_assignment(request.task_id, request.assignee_id,
                                                          status=request.status, score=request.score)
                session.flush()
                await stream.send_message(assignment.to_protobuf())
        except AssertionError:
            raise grpclib.GRPCError(status=grpclib.Status.FAILED_PRECONDITION, message="Unable to perform this update")
        except SQLAlchemyError as e:
            logging.error(e)
            raise grpclib.GRPCError(status=grpclib.Status.ABORTED, message="Could not update assignment")

    async def FindAssignmentById(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal() as session:
                repository = AssignmentRepository(session)
                assignment = repository.find_by_id(request.task_id, request.assignee_id)
                if not assignment:
                    raise grpclib.GRPCError(status=grpclib.Status.NOT_FOUND, message="No assignment with such id")
                await stream.send_message(assignment.to_protobuf())
        except SQLAlchemyError as e:
            logging.error(e)
            raise grpclib.GRPCError(status=grpclib.Status.ABORTED, message="Could not find assignment")

    async def FindAssignments(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal() as session:
                repository = AssignmentRepository(session)
                assignments, total_count = repository.find_assignments(request.task_id, limit=request.limit,
                                                                       offset=request.offset)
                await stream.send_message(assignment_pb2.AssignmentFindResponse(results=[assignment.to_protobuf()
                                                                                         for assignment in assignments],
                                                                                total_count=total_count))
        except SQLAlchemyError as e:
            logging.error(e)
            raise grpclib.GRPCError(status=grpclib.Status.ABORTED, message="Could not find assignments")

    async def CreateReview(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal.begin() as session:
                repository = AssignmentRepository(session)
                repository.update_assignment(request.task_id, request.assignee_id,
                                             score=request.score,
                                             status=AssignmentStatusEnum.APPROVED
                                             if request.approved else AssignmentStatusEnum.CHANGES_REQUESTED)
                review = Review(task_id=request.task_id,
                                assignee_id=request.assignee_id,
                                author_id=request.author_id,
                                approved=request.approved,
                                comment=request.comment if request.comment else None,
                                score=request.score if request.score else None)
                session.add(review)
                session.flush()
                await stream.send_message(review.to_protobuf())
        except AssertionError:
            raise grpclib.GRPCError(status=grpclib.Status.FAILED_PRECONDITION, message="Unable to perform this update")
        except SQLAlchemyError as e:
            logging.error(e)
            raise grpclib.GRPCError(status=grpclib.Status.ABORTED, message="Could not create review")

    async def FindReviews(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal() as session:
                repository = AssignmentRepository(session)
                reviews, total_count = repository.find_reviews(request.task_id, request.assignee_id,
                                                               limit=request.limit, offset=request.offset)
                await stream.send_message(review_pb2.ReviewFindResponse(results=[review.to_protobuf()
                                                                                 for review in reviews],
                                                                        total_count=total_count))
        except SQLAlchemyError as e:
            logging.error(e)
            raise grpclib.GRPCError(status=grpclib.Status.ABORTED, message="Could not find reviews")

    async def CreateAttempt(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal.begin() as session:
                repository = AssignmentRepository(session)
                repository.update_assignment(request.task_id, request.assignee_id,
                                             status=AssignmentStatusEnum.ATTEMPT_UPLOADED)
                attempt = Attempt(id=request.id,
                                  task_id=request.task_id,
                                  assignee_id=request.assignee_id)
                session.add(attempt)
                session.flush()
                await stream.send_message(attempt.to_protobuf())
        except AssertionError:
            raise grpclib.GRPCError(status=grpclib.Status.FAILED_PRECONDITION, message="Unable to perform this update")
        except SQLAlchemyError as e:
            logging.error(e)
            raise grpclib.GRPCError(status=grpclib.Status.ABORTED, message="Could not create attempt")

    async def FindAttempts(self, stream: grpclib.server.Stream):
        try:
            request = await stream.recv_message()
            with SessionLocal() as session:
                repository = AssignmentRepository(session)
                attempts, total_count = repository.find_attempts(request.task_id, request.assignee_id,
                                                                 limit=request.limit, offset=request.offset)
                await stream.send_message(attempt_pb2.AttemptFindResponse(results=[attempt.to_protobuf()
                                                                                   for attempt in attempts],
                                                                          total_count=total_count))
        except SQLAlchemyError as e:
            logging.error(e)
            raise grpclib.GRPCError(status=grpclib.Status.ABORTED, message="Could not find attempts")
