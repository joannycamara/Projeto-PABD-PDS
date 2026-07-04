from dataclasses import dataclass
from typing import Optional


@dataclass
class Titulo:
    """Representa a ficha bibliográfica (título) — dados compartilhados por
    todos os exemplares daquele livro."""

    id: Optional[int]
    titulo: str
    autor: str
    genero: str
    isbn: str


@dataclass
class Livros:
    """Representa um EXEMPLAR (cópia física) já com os dados do título
    embutidos, para manter compatibilidade com o restante do sistema
    (telas de aluno/bolsista/bibliotecário continuam lendo .titulo,
    .autor, .isbn, .genero, .disponivel normalmente)."""

    id: Optional[int]            # id do exemplar
    titulo: str
    autor: str
    genero: str
    isbn: str
    disponivel: bool = True
    id_titulo: Optional[int] = None   # id da ficha bibliográfica (titulos.id)