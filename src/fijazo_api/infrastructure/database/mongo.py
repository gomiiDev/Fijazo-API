"""Conexión a MongoDB usando el driver async oficial de PyMongo."""

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase


def create_client(mongo_uri: str) -> AsyncMongoClient:
    """Crea un cliente async de MongoDB.

    ``tz_aware=True`` hace que las fechas leídas vuelvan como *aware* (UTC), de
    modo que se pueden comparar con ``datetime.now(timezone.utc)`` sin errores.
    """

    return AsyncMongoClient(mongo_uri, tz_aware=True)


def get_database(client: AsyncMongoClient, db_name: str) -> AsyncDatabase:
    """Devuelve la base de datos indicada del cliente."""

    return client[db_name]


async def ensure_indexes(db: AsyncDatabase) -> None:
    """Crea los índices necesarios (idempotente).

    - ``users.email`` y ``users.username`` únicos (refuerza la unicidad).
    - ``bets.user_id`` para acelerar el listado por usuario.
    - ``user_statistics.user_id`` único y ``ranking_score`` (desc) para el ranking.
    """

    await db["users"].create_index("email", unique=True)
    await db["users"].create_index("username", unique=True)
    await db["bets"].create_index("user_id")
    await db["bets"].create_index(
        [("user_id", 1), ("reference_id", 1)],
        sparse=True,
    )
    await db["user_statistics"].create_index("user_id", unique=True)
    await db["user_statistics"].create_index([("ranking_score", -1)])
    await db["user_progression"].create_index("user_id", unique=True)
