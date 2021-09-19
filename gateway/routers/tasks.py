from fastapi import APIRouter

router = APIRouter(prefix="/tasks")


@router.get("/{id}")
async def get_task_by_id(id: str):
    pass


@router.get("/")
async def get_tasks():
    pass


@router.post("/")
async def create_task():
    pass


@router.get("/{id}/assignments")
async def get_task_assignments(id: str):
    pass


@router.get("/{task_id}/assignments/{assignment_id}")
async def get_assignment_by_id(task_id: str, assignment_id: str):
    pass


@router.get("/{task_id}/assignments/{assignment_id}/history")
async def get_assignment_history(task_id: str, assignment_id: str):
    pass
