from dataclasses import dataclass
from typing import Optional


@dataclass
class Emprestimos:
    """Representa a entidade de dominio Produto."""

    id: Optional[int]
    id_usuario: Optional[int]
    id_livro: Optional[int]
    data_emprestimo: str
    data_devolucao: str
    renovado: bool