from fastapi import APIRouter

router = APIRouter(prefix="/users")


@router.get("/{id}")
async def get_user_by_id(id: str):
    pass


@router.get("/me")
async def get_current_user():
    pass
