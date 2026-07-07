from dataclasses import dataclass
from typing import Optional


@dataclass
class Emprestimos:
    """Representa a entidade de dominio Produto."""

    id: Optional[int]
    id_usuario: Optional[int]
    id_livro: Optional[int]
    data_emprestimo: str
    data_devolucao: str          # data PREVISTA (prazo)
    renovado: bool
    data_devolucao_real: Optional[str] = None  # preenchida só quando devolvido