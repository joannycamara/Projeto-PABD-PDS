from dataclasses import dataclass
from typing import Optional


@dataclass
class Usuarios:
    """Representa a entidade de dominio Produto."""

    id: Optional[int]
    nome: str
    senha: str
    tipo: str