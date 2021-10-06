from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from gateway.dependencies.auth import authorized
from gateway.dependencies.courses import CoursesContext
from gateway.dependencies.tasks import TasksContext
from gateway.schemas.assignment import AssignmentStatusEnum
from gateway.schemas.reports.academic_performance import AcademicPerformanceReport, AcademicPerformanceReportRow
from gateway.schemas.user import RoleEnum

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/academic_performance", response_model=AcademicPerformanceReport)
async def get_academic_performance(course_id: UUID,
                                   courses: CoursesContext = Depends(),
                                   tasks: TasksContext = Depends(),
                                   user=Depends(authorized)):
    if user["role"] != RoleEnum.admin and user["role"] != RoleEnum.teacher:
        raise HTTPException(status_code=403)
    if not await courses.find_course_by_id(course_id):
        raise HTTPException(status_code=404)
    tasks_page = await tasks.find_tasks(user_id=user["uid"], course_id=course_id, limit=0)
    tasks_page = await tasks.find_tasks(user_id=user["uid"], course_id=course_id, limit=tasks_page.total_count)
    users_dict = {}
    for task in tasks_page.results:
        assignments_page = await tasks.find_assignments(task.id, limit=0)
        assignments_page = await tasks.find_assignments(task.id, limit=assignments_page.total_count)
        for assignment in assignments_page.results:
            if assignment.assignee.id not in users_dict:
                users_dict[assignment.assignee.id] = AcademicPerformanceReportRow(
                    user=assignment.assignee,
                    scores=[]
                )
            score = assignment.score if assignment.status == AssignmentStatusEnum.APPROVED else None
            users_dict[assignment.assignee.id].scores.append(score)
    rows = sorted(users_dict.values(), key=lambda row: row.user.name)
    return AcademicPerformanceReport(tasks=tasks_page.results, rows=rows)

