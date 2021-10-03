import logging

import grpc
from sqlalchemy.exc import SQLAlchemyError

from tasks.db import SessionLocal
from tasks.models.assignment import Assignment, AssignmentStatusEnum
from tasks.models.attempt import Attempt
from tasks.models.review import Review
from tasks.models.task import Task
from tasks.proto import assignment_pb2, attempt_pb2, review_pb2, task_pb2
from tasks.proto.tasks_pb2_grpc import TasksServicer

from tasks.repository.assignment import AssignmentRepository
from tasks.repository.task import TaskRepository


class TasksService(TasksServicer):
    def CreateTask(self, request: task_pb2.TaskCreateRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal.begin() as session:
                task = Task(name=request.name,
                            description=request.description if request.description else None,
                            author_id=request.author_id,
                            course_id=request.course_id)
                session.add(task)
                session.flush()
                return task.to_protobuf()
        except SQLAlchemyError as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not create task")

    def FindTaskById(self, request: task_pb2.TaskFindByIdRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal() as session:
                repository = TaskRepository(session)
                task = repository.find_by_id(request.id)
                if not task:
                    context.abort(grpc.StatusCode.NOT_FOUND, "No task with such id")
                return task.to_protobuf()
        except SQLAlchemyError as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not find task")

    def FindTasks(self, request: task_pb2.TaskFindRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal() as session:
                repository = TaskRepository(session)
                tasks, total_count = repository.find_tasks(user_id=request.user_id, course_id=request.user_id,
                                                           limit=request.limit, offset=request.offset)
                return task_pb2.TaskFindResponse(results=[task.to_protobuf() for task in tasks],
                                                 total_count=total_count)
        except SQLAlchemyError as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not find tasks")

    def CreateAssignment(self, request: assignment_pb2.AssignmentCreateRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal.begin() as session:
                assignment = Assignment(task_id=request.task_id, assignee_id=request.assignee_id)
                session.add(assignment)
                session.flush()
                return assignment.to_protobuf()
        except SQLAlchemyError as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not create assignment")

    def UpdateAssignment(self, request: assignment_pb2.AssignmentUpdateRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal.begin() as session:
                repository = AssignmentRepository(session)
                assignment = repository.update_assignment(request.task_id, request.assignee_id,
                                                          status=request.status, score=request.score)
                session.flush()
                return assignment.to_protobuf()
        except AssertionError:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Unable to perform this update")
        except SQLAlchemyError as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not update assignment")

    def FindAssignmentById(self, request: assignment_pb2.AssignmentFindByIdRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal() as session:
                repository = AssignmentRepository(session)
                assignment = repository.find_by_id(request.task_id, request.assignee_id)
                if not assignment:
                    context.abort(grpc.StatusCode.NOT_FOUND, "No assignment with such id")
                return assignment.to_protobuf()
        except SQLAlchemyError as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not find assignment")

    def FindAssignments(self, request: assignment_pb2.AssignmentFindRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal() as session:
                repository = AssignmentRepository(session)
                assignments, total_count = repository.find_assignments(request.task_id, limit=request.limit,
                                                                       offset=request.offset)
                return assignment_pb2.AssignmentFindResponse(results=[assignment.to_protobuf()
                                                                      for assignment in assignments],
                                                             total_count=total_count)
        except SQLAlchemyError as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not find assignments")

    def CreateReview(self, request: review_pb2.ReviewCreateRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal.begin() as session:
                repository = AssignmentRepository(session)
                repository.update_assignment(request.task_id, request.assignee_id,
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
                return review.to_protobuf()
        except AssertionError:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Unable to perform this update")
        except SQLAlchemyError as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not create review")

    def FindReviews(self, request: review_pb2.ReviewFindRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal() as session:
                repository = AssignmentRepository(session)
                reviews, total_count = repository.find_reviews(request.task_id, request.assignee_id,
                                                               limit=request.limit, offset=request.offset)
                return review_pb2.ReviewFindResponse(results=[review.to_protobuf() for review in reviews],
                                                     total_count=total_count)
        except SQLAlchemyError as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not find reviews")

    def CreateAttempt(self, request: attempt_pb2.AttemptCreateRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal.begin() as session:
                repository = AssignmentRepository(session)
                repository.update_assignment(request.task_id, request.assignee_id,
                                             status=AssignmentStatusEnum.ATTEMPT_UPLOADED)
                attempt = Attempt(id=request.id,
                                  task_id=request.task_id,
                                  assignee_id=request.assignee_id)
                session.add(attempt)
                session.flush()
                return attempt.to_protobuf()
        except AssertionError:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Unable to perform this update")
        except SQLAlchemyError as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not create attempt")

    def FindAttempts(self, request: attempt_pb2.AttemptFindRequest, context: grpc.ServicerContext):
        try:
            with SessionLocal() as session:
                repository = AssignmentRepository(session)
                attempts, total_count = repository.find_attempts(request.task_id, request.assignee_id,
                                                                 limit=request.limit, offset=request.offset)
                return review_pb2.ReviewFindResponse(results=[attempt.to_protobuf() for attempt in attempts],
                                                     total_count=total_count)
        except SQLAlchemyError as e:
            logging.error(e)
            context.abort(grpc.StatusCode.ABORTED, "Could not find attempts")
