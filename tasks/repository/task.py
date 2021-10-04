from typing import Optional
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from tasks.models.assignment import Assignment
from tasks.models.task import Task


class TaskRepository:
    def __init__(self, session: Session):
        self._session = session

    def find_by_id(self, id: UUID):
        return self._session.query(Task).get(id)

    def find_tasks(self, user_id: Optional[UUID] = None, course_id: Optional[UUID] = None,
                   limit: int = 10, offset: int = 0):
        query = self._session.query(Task)
        if course_id:
            query = query.filter_by(course_id=course_id)
        if user_id:
            query = query.join(Assignment, isouter=True).filter(or_(Task.author_id == user_id,
                                                                    Assignment.assignee_id == user_id))
        return query.offset(offset).limit(limit).all(), query.order_by(None).count()


