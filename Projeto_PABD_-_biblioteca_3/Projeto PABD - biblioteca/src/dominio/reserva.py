from dataclasses import dataclass
from typing import Optional


@dataclass
class Reserva:
    """Representa a entidade de domínio Reserva."""

    id: Optional[int]
    id_usuario: int
    id_livro: int
    data_reserva: str
    ativa: bool
