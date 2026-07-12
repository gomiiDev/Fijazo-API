"""Schemas Pydantic para usuarios."""

from datetime import datetime

from pydantic import BaseModel

from fijazo_api.domain.entities.user import Role, User


class UserResponse(BaseModel):
    """Representación pública de un usuario (sin contraseña)."""

    id: str
    username: str
    email: str
    role: Role
    created_at: datetime

    @classmethod
    def from_entity(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id or "",
            username=user.username,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
        )
