"""Casos de uso de autenticación: registro e inicio de sesión."""

from fijazo_api.core.exceptions import AlreadyExistsError, InvalidCredentialsError
from fijazo_api.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from fijazo_api.domain.entities.user import Role, User
from fijazo_api.domain.repositories.user_repository import UserRepository


class AuthService:
    """Reglas de negocio para autenticación de usuarios."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    async def register(self, username: str, email: str, password: str) -> User:
        """Registra un nuevo usuario con rol ``USER``.

        Valida que el email y el username no estén ya en uso.
        """

        if await self._users.get_by_email(email) is not None:
            raise AlreadyExistsError("El correo electrónico ya está registrado.")
        if await self._users.get_by_username(username) is not None:
            raise AlreadyExistsError("El nombre de usuario ya está en uso.")

        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            role=Role.USER,
        )
        return await self._users.create(user)

    async def login(self, email: str, password: str) -> str:
        """Valida credenciales y devuelve un JWT de acceso."""

        user = await self._users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Correo o contraseña incorrectos.")

        assert user.id is not None  # persistido: siempre tiene id
        return create_access_token(subject=user.id, role=user.role.value)
