"""Puertos (interfaces) de la capa de aplicación.

Permiten que un caso de uso dependa de una capacidad abstracta en lugar de una
implementación concreta, evitando acoplamiento y ciclos de import.
"""

from typing import Protocol


class StatisticsSynchronizer(Protocol):
    """Capacidad de recalcular las estadísticas de un usuario.

    La implementa :class:`StatisticsService`. ``BetService`` la usa para
    mantener el ranking sincronizado tras cada mutación de apuestas.
    """

    async def recalculate(self, user_id: str) -> None: ...
