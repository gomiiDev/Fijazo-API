"""Configuración de la aplicación cargada desde variables de entorno / .env."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Ajustes de la aplicación.

    Los valores se leen de variables de entorno (o de un archivo ``.env``).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Aplicación
    app_name: str = "Fijazo API"
    app_description: str = (
        "API para gestionar apuestas deportivas y el historial personal de cada usuario."
    )
    app_version: str = "0.1.0"

    # MongoDB
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "fijazo"

    # Seguridad / JWT
    jwt_secret: str = "change-me-in-production-please-use-a-secure-random-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # Usuario administrador inicial (seed)
    admin_username: str = "admin"
    admin_email: str = "admin@fijazo.local"
    admin_password: str = "changeme123"


@lru_cache
def get_settings() -> Settings:
    """Devuelve una instancia cacheada de :class:`Settings`."""

    return Settings()
