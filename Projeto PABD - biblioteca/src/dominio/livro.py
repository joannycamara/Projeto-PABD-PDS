from dataclasses import dataclass
from typing import Optional


@dataclass
class Livros:
    """Representa a entidade de dominio Produto."""

    id: Optional[int]
    titulo: str
    autor: str
    genero: str
    disponivel: bool