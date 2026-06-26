from dataclasses import dataclass
from typing import Optional


@dataclass
class Livros:
    """Representa a entidade de domínio Livros."""

    id: Optional[int]
    titulo: str
    autor: str
    genero: str
    isbn: str
    disponivel: bool = True