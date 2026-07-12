"""Punto de entrada de la aplicación FastAPI (app factory)."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from fijazo_api.api.routers import (
    achievements,
    auth,
    bets,
    ranking,
    ranks,
    statistics,
    users,
)
from fijazo_api.application.services.progression_service import ProgressionService
from fijazo_api.application.services.statistics_service import StatisticsService
from fijazo_api.core.config import get_settings
from fijazo_api.core.exceptions import (
    AlreadyExistsError,
    DomainError,
    ForbiddenError,
    InvalidCredentialsError,
    NotFoundError,
)
from fijazo_api.infrastructure.database.mongo import (
    create_client,
    ensure_indexes,
    get_database,
)
from fijazo_api.infrastructure.repositories.mongo_bet_repository import (
    MongoBetRepository,
)
from fijazo_api.infrastructure.repositories.mongo_progression_repository import (
    MongoProgressionRepository,
)
from fijazo_api.infrastructure.repositories.mongo_statistics_repository import (
    MongoStatisticsRepository,
)
from fijazo_api.infrastructure.repositories.mongo_user_repository import (
    MongoUserRepository,
)
from fijazo_api.infrastructure.seed import seed_admin

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona la conexión a MongoDB, índices y seed durante el ciclo de vida."""

    settings = get_settings()
    client = create_client(settings.mongo_uri)
    db = get_database(client, settings.mongo_db_name)

    app.state.mongo_client = client
    app.state.db = db

    user_repo = MongoUserRepository(db)
    await ensure_indexes(db)
    await seed_admin(user_repo, settings)

    # Backfill idempotente: estadísticas + rango/logros de las apuestas existentes.
    bet_repo = MongoBetRepository(db)
    stats_service = StatisticsService(bet_repo, MongoStatisticsRepository(db), user_repo)
    progression_service = ProgressionService(
        stats_service, MongoProgressionRepository(db), user_repo, bet_repo
    )
    processed = await progression_service.recalculate_all()
    logger.info("Backfill de estadísticas y progresión completado para %d usuario(s).", processed)

    try:
        yield
    finally:
        await client.close()


def _register_exception_handlers(app: FastAPI) -> None:
    """Traduce las excepciones de dominio a respuestas HTTP uniformes."""

    status_map: dict[type[DomainError], int] = {
        NotFoundError: 404,
        AlreadyExistsError: 409,
        InvalidCredentialsError: 401,
        ForbiddenError: 403,
    }

    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        status_code = status_map.get(type(exc), 400)
        headers = {"WWW-Authenticate": "Bearer"} if status_code == 401 else None
        return JSONResponse(
            status_code=status_code,
            content={"detail": exc.message},
            headers=headers,
        )

    app.add_exception_handler(DomainError, domain_error_handler)


def create_app() -> FastAPI:
    """Construye y configura la aplicación FastAPI."""

    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        lifespan=lifespan,
    )

    _register_exception_handlers(app)

    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(bets.router)
    app.include_router(statistics.router)
    app.include_router(ranking.router)
    app.include_router(achievements.router)
    app.include_router(ranks.router)

    @app.get("/health", tags=["health"], summary="Comprobación de salud")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
