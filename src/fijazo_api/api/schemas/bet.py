"""Schemas Pydantic para apuestas."""

from datetime import datetime

from pydantic import BaseModel, Field

from fijazo_api.domain.entities.bet import Bet, BetStatus, BetType


class BetCreate(BaseModel):
    """Cuerpo para crear una apuesta.

    Los campos calculados no se aceptan aquí: el servicio los deriva de
    ``stake`` y ``odds``.
    """

    sport: str = Field(min_length=1, max_length=100)
    league: str = Field(min_length=1, max_length=100)
    event: str = Field(min_length=1, max_length=200)
    bet_type: BetType
    market: str = Field(min_length=1, max_length=100)
    selection: str = Field(min_length=1, max_length=200)
    odds: float = Field(gt=1, description="Cuota decimal, debe ser mayor que 1.")
    stake: float = Field(gt=0, description="Inversión, debe ser mayor que 0.")
    bookmaker: str = Field(min_length=1, max_length=100)
    event_datetime: datetime
    status: BetStatus = BetStatus.PENDING
    notes: str | None = Field(default=None, max_length=1000)
    reference_id: str | None = Field(default=None, max_length=100)


class BetUpdate(BaseModel):
    """Cuerpo para actualizar una apuesta. Todos los campos son opcionales."""

    sport: str | None = Field(default=None, min_length=1, max_length=100)
    league: str | None = Field(default=None, min_length=1, max_length=100)
    event: str | None = Field(default=None, min_length=1, max_length=200)
    bet_type: BetType | None = None
    market: str | None = Field(default=None, min_length=1, max_length=100)
    selection: str | None = Field(default=None, min_length=1, max_length=200)
    odds: float | None = Field(default=None, gt=1)
    stake: float | None = Field(default=None, gt=0)
    bookmaker: str | None = Field(default=None, min_length=1, max_length=100)
    event_datetime: datetime | None = None
    status: BetStatus | None = None
    notes: str | None = Field(default=None, max_length=1000)
    reference_id: str | None = Field(default=None, max_length=100)


class BetResponse(BaseModel):
    """Representación de una apuesta, incluyendo campos calculados."""

    id: str
    sport: str
    league: str
    event: str
    bet_type: BetType
    market: str
    selection: str
    odds: float
    stake: float
    bookmaker: str
    event_datetime: datetime
    status: BetStatus
    notes: str | None
    reference_id: str | None
    potential_return: float
    potential_profit: float
    implied_probability: float
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, bet: Bet) -> "BetResponse":
        return cls(
            id=bet.id or "",
            sport=bet.sport,
            league=bet.league,
            event=bet.event,
            bet_type=bet.bet_type,
            market=bet.market,
            selection=bet.selection,
            odds=bet.odds,
            stake=bet.stake,
            bookmaker=bet.bookmaker,
            event_datetime=bet.event_datetime,
            status=bet.status,
            notes=bet.notes,
            reference_id=bet.reference_id,
            potential_return=bet.potential_return,
            potential_profit=bet.potential_profit,
            implied_probability=bet.implied_probability,
            created_at=bet.created_at,
            updated_at=bet.updated_at,
        )


class PaginatedBets(BaseModel):
    """Resultado paginado de apuestas."""

    items: list[BetResponse]
    total: int
    page: int
    page_size: int
