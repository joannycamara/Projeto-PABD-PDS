from dataclasses import dataclass
from typing import Optional


@dataclass
class SolicitacaoEmprestimo:
    """Representa um pedido de empréstimo feito pelo aluno, que precisa ser
    aprovado (ou rejeitado) pelo bolsista antes de virar um empréstimo real."""

    id: Optional[int]
    id_usuario: int
    id_livro: int
    data_solicitacao: str
    status: str = "pendente"  # pendente | aprovada | rejeitada

    @property
    def pendente(self) -> bool:
        return self.status == "pendente"
