"""Caso de uso: importar apuestas desde filas de un Excel.

Orquesta la validación y creación reutilizando las reglas existentes:
* ``BetCreate`` (schema Pydantic) como única fuente de validación de campos.
* ``BetService.create_bet`` para crear cada apuesta (calcula derivados y
  sincroniza estadísticas/ranking).

No contiene lógica de lectura de Excel: recibe filas ya leídas por el adaptador
de infraestructura.
"""

from dataclasses import dataclass, field
from typing import Any

from pydantic import ValidationError

from fijazo_api.api.schemas.bet import BetCreate
from fijazo_api.application.services.bet_service import BetService
from fijazo_api.domain.repositories.bet_repository import BetRepository


@dataclass
class RowError:
    """Error asociado a una fila del archivo."""

    row: int
    field: str
    error: str


@dataclass
class ImportSummary:
    """Resumen del resultado de una importación."""

    total_rows: int = 0
    imported: int = 0
    rejected: int = 0
    errors: list[RowError] = field(default_factory=list)


class BetImportService:
    """Procesa filas de apuestas: valida, evita duplicados y crea cada apuesta."""

    def __init__(self, bet_service: BetService, bet_repository: BetRepository) -> None:
        self._bets = bet_service
        self._repo = bet_repository

    async def import_rows(
        self, user_id: str, rows: list[tuple[int, dict[str, Any]]]
    ) -> ImportSummary:
        """Importa las filas dadas para ``user_id`` y devuelve el resumen."""

        summary = ImportSummary(total_rows=len(rows))
        seen_keys: set[tuple] = set()
        seen_refs: set[str] = set()

        for row_number, record in rows:
            try:
                data = BetCreate(**record)
            except ValidationError as exc:
                for err in exc.errors():
                    loc = err.get("loc") or ()
                    field_name = str(loc[0]) if loc else ""
                    summary.errors.append(RowError(row_number, field_name, err["msg"]))
                summary.rejected += 1
                continue

            # Duplicados dentro del archivo (evento + selección + fecha).
            key = (data.event, data.selection, data.event_datetime)
            if key in seen_keys:
                summary.errors.append(
                    RowError(row_number, "evento", "Fila duplicada dentro del archivo.")
                )
                summary.rejected += 1
                continue
            seen_keys.add(key)

            # reference_id repetido en el archivo o ya existente en la BD.
            if data.reference_id:
                if data.reference_id in seen_refs:
                    summary.errors.append(
                        RowError(
                            row_number,
                            "reference_id",
                            "ID de referencia duplicado dentro del archivo.",
                        )
                    )
                    summary.rejected += 1
                    continue
                if await self._repo.reference_exists(user_id, data.reference_id):
                    summary.errors.append(
                        RowError(
                            row_number,
                            "reference_id",
                            "El ID de referencia ya existe para el usuario.",
                        )
                    )
                    summary.rejected += 1
                    continue
                seen_refs.add(data.reference_id)

            try:
                await self._bets.create_bet(user_id, data.model_dump())
            except Exception as exc:  # una fila mala no detiene el resto
                summary.errors.append(RowError(row_number, "", str(exc)))
                summary.rejected += 1
                continue

            summary.imported += 1

        return summary
