"""Router de usuarios: perfil del usuario autenticado."""

from fastapi import APIRouter

from fijazo_api.api.deps import CurrentUser
from fijazo_api.api.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener el perfil del usuario autenticado",
)
async def get_me(current_user: CurrentUser) -> UserResponse:
    return UserResponse.from_entity(current_user)
