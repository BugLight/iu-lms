from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from tasks.models.assignment import Assignment, AssignmentStatusEnum
from tasks.models.attempt import Attempt
from tasks.models.review import Review

STATUS_TRANSITIONS = {
    (AssignmentStatusEnum.ASSIGNED, AssignmentStatusEnum.ATTEMPT_UPLOADED),
    (AssignmentStatusEnum.ATTEMPT_UPLOADED, AssignmentStatusEnum.ATTEMPT_UPLOADED),
    (AssignmentStatusEnum.ATTEMPT_UPLOADED, AssignmentStatusEnum.APPROVED),
    (AssignmentStatusEnum.ATTEMPT_UPLOADED, AssignmentStatusEnum.CHANGES_REQUESTED),
    (AssignmentStatusEnum.APPROVED, AssignmentStatusEnum.APPROVED),
    (AssignmentStatusEnum.CHANGES_REQUESTED, AssignmentStatusEnum.ATTEMPT_UPLOADED),
    (AssignmentStatusEnum.CHANGES_REQUESTED, AssignmentStatusEnum.CHANGES_REQUESTED),
}


class AssignmentRepository:
    def __init__(self, session: Session):
        self._session = session

    def find_by_id(self, task_id: UUID, assignee_id: UUID):
        return self._session.query(Assignment).get({"task_id": task_id, "assignee_id": assignee_id})

    def find_assignments(self, task_id: UUID, limit: int = 10, offset: int = 0):
        query = self._session.query(Assignment).filter_by(task_id=task_id)
        return query.offset(offset).limit(limit).all(), query.order_by(None).count()

    def find_reviews(self, task_id: UUID, assignee_id: UUID, limit: int = 10, offset: int = 0):
        query = self._session.query(Review).join(Assignment).filter(and_(Assignment.task_id == task_id,
                                                                         Assignment.assignee_id == assignee_id))
        return query.offset(offset).limit(limit).all(), query.order_by(None).count()

    def find_attempts(self, task_id: UUID, assignee_id: UUID, limit: int = 10, offset: int = 0):
        query = self._session.query(Attempt).join(Assignment).filter(and_(Assignment.task_id == task_id,
                                                                          Assignment.assignee_id == assignee_id))
        return query.offset(offset).limit(limit).all(), query.order_by(None).count()

    def update_assignment(self, task_id: UUID, assignee_id: UUID,
                          status: Optional[AssignmentStatusEnum] = None,
                          score: Optional[int] = None):
        assignment = self.find_by_id(task_id, assignee_id)
        assert assignment
        if status:
            assert (assignment.status, status) in STATUS_TRANSITIONS
            assignment.status = status
        if score and assignment.status == AssignmentStatusEnum.APPROVED:
            assignment.score = score
        assignment.updated = datetime.utcnow()
        self._session.add(assignment)
        return assignment
