from dataclasses import dataclass
from typing import Optional


@dataclass
class Emprestimos:
    """Representa a entidade de dominio Produto."""

    id: Optional[int]
    id_usuario: Optional[int]
    id_livro: Optional[int]
    data_emprestimo: str
    data_devolucao: str                     # prazo (data prevista)
    renovado: bool
    data_devolucao_real: Optional[str] = None  # preenchida ao devolver de fato

    @property
    def ativo(self) -> bool:
        """True enquanto o livro não foi devolvido."""
        return self.data_devolucao_real is None