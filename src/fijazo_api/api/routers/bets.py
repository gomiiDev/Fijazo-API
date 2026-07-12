"""Router de apuestas: CRUD con paginación y filtros. Requiere autenticación."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from fijazo_api.api.deps import CurrentUser, get_bet_service
from fijazo_api.api.schemas.bet import (
    BetCreate,
    BetResponse,
    BetUpdate,
    PaginatedBets,
)
from fijazo_api.application.services.bet_service import BetService
from fijazo_api.domain.entities.bet import BetStatus, BetType

router = APIRouter(prefix="/bets", tags=["bets"])


@router.post(
    "",
    response_model=BetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una apuesta",
)
async def create_bet(
    body: BetCreate,
    current_user: CurrentUser,
    service: Annotated[BetService, Depends(get_bet_service)],
) -> BetResponse:
    bet = await service.create_bet(current_user.id, body.model_dump())
    return BetResponse.from_entity(bet)


@router.get(
    "",
    response_model=PaginatedBets,
    summary="Listar las apuestas del usuario con paginación y filtros",
)
async def list_bets(
    current_user: CurrentUser,
    service: Annotated[BetService, Depends(get_bet_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    status_filter: Annotated[BetStatus | None, Query(alias="status")] = None,
    sport: str | None = None,
    bet_type: BetType | None = None,
) -> PaginatedBets:
    items, total = await service.list_bets(
        current_user.id,
        page=page,
        page_size=page_size,
        status=status_filter,
        sport=sport,
        bet_type=bet_type,
    )
    return PaginatedBets(
        items=[BetResponse.from_entity(b) for b in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{bet_id}",
    response_model=BetResponse,
    summary="Obtener una apuesta por su ID",
)
async def get_bet(
    bet_id: str,
    current_user: CurrentUser,
    service: Annotated[BetService, Depends(get_bet_service)],
) -> BetResponse:
    bet = await service.get_bet(current_user.id, bet_id)
    return BetResponse.from_entity(bet)


@router.put(
    "/{bet_id}",
    response_model=BetResponse,
    summary="Editar una apuesta",
)
async def update_bet(
    bet_id: str,
    body: BetUpdate,
    current_user: CurrentUser,
    service: Annotated[BetService, Depends(get_bet_service)],
) -> BetResponse:
    changes = body.model_dump(exclude_unset=True)
    bet = await service.update_bet(current_user.id, bet_id, changes)
    return BetResponse.from_entity(bet)


@router.delete(
    "/{bet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una apuesta",
)
async def delete_bet(
    bet_id: str,
    current_user: CurrentUser,
    service: Annotated[BetService, Depends(get_bet_service)],
) -> None:
    await service.delete_bet(current_user.id, bet_id)
