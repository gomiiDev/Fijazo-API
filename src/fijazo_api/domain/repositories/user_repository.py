"""Interfaz abstracta del repositorio de usuarios."""

from abc import ABC, abstractmethod

from fijazo_api.domain.entities.user import User


class UserRepository(ABC):
    """Contrato de persistencia para :class:`User`.

    La capa de aplicación depende de esta abstracción, no de la implementación
    concreta de MongoDB.
    """

    @abstractmethod
    async def create(self, user: User) -> User:
        """Persiste un nuevo usuario y devuelve la entidad con su ``id``."""

    @abstractmethod
    async def get_by_id(self, user_id: str) -> User | None:
        """Devuelve el usuario con el id dado, o ``None``."""

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Devuelve el usuario con el email dado, o ``None``."""

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        """Devuelve el usuario con el username dado, o ``None``."""
