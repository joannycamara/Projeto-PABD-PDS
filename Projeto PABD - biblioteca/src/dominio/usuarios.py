from dataclasses import dataclass
from typing import Optional


@dataclass
class Usuarios:
    """Representa a entidade de domínio Usuarios."""

    id: Optional[int]
    nome: str
    email: str
    senha: str
    tipo: str  # 'aluno' | 'bolsista' | 'bibliotecario'