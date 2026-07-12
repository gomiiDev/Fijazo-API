"""Conexión a MongoDB usando el driver async oficial de PyMongo."""

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase


def create_client(mongo_uri: str) -> AsyncMongoClient:
    """Crea un cliente async de MongoDB."""

    return AsyncMongoClient(mongo_uri)


def get_database(client: AsyncMongoClient, db_name: str) -> AsyncDatabase:
    """Devuelve la base de datos indicada del cliente."""

    return client[db_name]


async def ensure_indexes(db: AsyncDatabase) -> None:
    """Crea los índices necesarios (idempotente).

    - ``users.email`` y ``users.username`` únicos (refuerza la unicidad).
    - ``bets.user_id`` para acelerar el listado por usuario.
    """

    await db["users"].create_index("email", unique=True)
    await db["users"].create_index("username", unique=True)
    await db["bets"].create_index("user_id")
