"""Casos de uso de apuestas: CRUD con campos calculados y control de propiedad."""

from datetime import datetime, timezone
from typing import Any

from fijazo_api.application.ports import StatisticsSynchronizer
from fijazo_api.core.exceptions import NotFoundError
from fijazo_api.domain.entities.bet import Bet, BetStatus, BetType
from fijazo_api.domain.repositories.bet_repository import BetRepository


class BetService:
    """Reglas de negocio para la gestión de apuestas.

    Toda operación sobre una apuesta concreta valida que pertenezca al usuario
    autenticado; en caso contrario se comporta como si no existiera (404),
    evitando filtrar la existencia de recursos ajenos.

    Si se le inyecta un ``StatisticsSynchronizer``, tras cada mutación recalcula
    las estadísticas del usuario para mantener el ranking sincronizado.
    """

    def __init__(
        self,
        bet_repository: BetRepository,
        stats_sync: StatisticsSynchronizer | None = None,
    ) -> None:
        self._bets = bet_repository
        self._stats_sync = stats_sync

    async def _sync_stats(self, user_id: str) -> None:
        if self._stats_sync is not None:
            await self._stats_sync.recalculate(user_id)

    async def create_bet(self, user_id: str, data: dict[str, Any]) -> Bet:
        """Crea una apuesta para el usuario y calcula los campos derivados."""

        bet = Bet(user_id=user_id, **data)
        bet.recalculate()
        created = await self._bets.create(bet)
        await self._sync_stats(user_id)
        return created

    async def get_bet(self, user_id: str, bet_id: str) -> Bet:
        """Devuelve una apuesta del usuario o lanza :class:`NotFoundError`."""

        bet = await self._bets.get_by_id(bet_id)
        if bet is None or bet.user_id != user_id:
            raise NotFoundError("Apuesta no encontrada.")
        return bet

    async def list_bets(
        self,
        user_id: str,
        *,
        page: int = 1,
        page_size: int = 20,
        status: BetStatus | None = None,
        sport: str | None = None,
        bet_type: BetType | None = None,
    ) -> tuple[list[Bet], int]:
        """Lista las apuestas del usuario con paginación y filtros."""

        skip = (page - 1) * page_size
        return await self._bets.list_by_user(
            user_id,
            skip=skip,
            limit=page_size,
            status=status,
            sport=sport,
            bet_type=bet_type,
        )

    async def update_bet(self, user_id: str, bet_id: str, changes: dict[str, Any]) -> Bet:
        """Actualiza los campos indicados de una apuesta del usuario."""

        bet = await self.get_bet(user_id, bet_id)

        for key, value in changes.items():
            setattr(bet, key, value)

        bet.recalculate()
        bet.updated_at = datetime.now(timezone.utc)
        updated = await self._bets.update(bet)
        await self._sync_stats(user_id)
        return updated

    async def delete_bet(self, user_id: str, bet_id: str) -> None:
        """Elimina una apuesta del usuario o lanza :class:`NotFoundError`."""

        # Reutiliza get_bet para verificar propiedad y existencia.
        await self.get_bet(user_id, bet_id)
        await self._bets.delete(bet_id)
        await self._sync_stats(user_id)
