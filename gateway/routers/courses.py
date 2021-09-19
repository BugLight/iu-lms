from fastapi import APIRouter

router = APIRouter(prefix="/courses")


@router.get("/{id}")
async def get_course_by_id(id: str):
    pass


@router.get("/")
async def get_courses():
    pass


@router.post("/")
async def create_course():
    pass


@router.delete("/{id}")
async def delete_course(id: str):
    pass


@router.get("/{id}/access")
async def get_access(id: str):
    pass


@router.put("/{id}/access")
async def modify_access(id: str):
    pass
