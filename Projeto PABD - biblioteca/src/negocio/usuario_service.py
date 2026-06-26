from typing import Optional

from dados.usuarios_repository import UsuariosRepository
from dominio.usuarios import Usuarios

TIPOS_VALIDOS = {"aluno", "bolsista", "bibliotecario"}
MAX_TENTATIVAS_LOGIN = 5

_tentativas_falhas: dict[str, int] = {}


class UsuarioService:
    """Camada de negócio: regras relacionadas a usuários (US01, US02, US03)."""

    def __init__(self, repositorio: UsuariosRepository) -> None:
        self.repositorio = repositorio

    # ------------------------------------------------------------------
    # US01 — Cadastro de Usuário
    # ------------------------------------------------------------------

    def cadastrar_usuario(self, nome: str, email: str, senha: str, tipo: str) -> Usuarios:
        nome_limpo = nome.strip()
        email_limpo = email.strip().lower()
        tipo_limpo = tipo.strip().lower()

        if not nome_limpo:
            raise ValueError("O nome não pode ficar vazio.")

        if not email_limpo:
            raise ValueError("O e-mail não pode ficar vazio.")

        if len(senha) < 5:
            raise ValueError("A senha deve ter no mínimo 5 caracteres.")

        if tipo_limpo not in TIPOS_VALIDOS:
            raise ValueError(f"Tipo inválido. Use: {', '.join(TIPOS_VALIDOS)}.")

        if self.repositorio.buscar_por_email(email_limpo) is not None:
            raise ValueError("Já existe um usuário cadastrado com este e-mail.")

        usuario = Usuarios(id=None, nome=nome_limpo, email=email_limpo, senha=senha, tipo=tipo_limpo)
        novo_id = self.repositorio.adicionar(usuario)
        usuario.id = novo_id
        return usuario

    # ------------------------------------------------------------------
    # US02 — Login
    # ------------------------------------------------------------------

    def login(self, email: str, senha: str) -> Usuarios:
        email_limpo = email.strip().lower()

        if not email_limpo:
            raise ValueError("Informe o e-mail.")

        if not senha:
            raise ValueError("Informe a senha.")

        tentativas = _tentativas_falhas.get(email_limpo, 0)
        if tentativas >= MAX_TENTATIVAS_LOGIN:
            raise ValueError("Muitas tentativas. Tente novamente em alguns minutos.")

        usuario = self.repositorio.buscar_por_email(email_limpo)

        if usuario is None or usuario.senha != senha:
            _tentativas_falhas[email_limpo] = tentativas + 1
            raise ValueError("E-mail ou senha inválidos.")

        # Login bem-sucedido: limpa contador de tentativas
        _tentativas_falhas.pop(email_limpo, None)
        return usuario

    # ------------------------------------------------------------------
    # US03 — Logout (controle de sessão simples)
    # ------------------------------------------------------------------

    def logout(self, email: str) -> None:
        """Encerra a sessão do usuário. A camada de apresentação deve
        descartar o objeto de sessão após esta chamada."""
        # Regra de negócio: apenas confirma que o usuário existe
        email_limpo = email.strip().lower()
        if not self.repositorio.buscar_por_email(email_limpo):
            raise ValueError("Usuário não encontrado.")

    # ------------------------------------------------------------------
    # Operações gerais (suporte a US11 e US06)
    # ------------------------------------------------------------------

    def buscar_por_id(self, id_usuario: int) -> Optional[Usuarios]:
        if id_usuario <= 0:
            raise ValueError("O ID deve ser um número inteiro positivo.")
        return self.repositorio.buscar_por_id(id_usuario)

    def buscar_por_nome(self, nome: str) -> list[Usuarios]:
        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("Informe um nome para a busca.")
        return self.repositorio.buscar_por_nome(nome_limpo)

    def listar_usuarios(self) -> list[Usuarios]:
        return self.repositorio.listar_todos()

    def atualizar_usuario(self, id_usuario: int, nome: str, email: str, senha: str, tipo: str) -> bool:
        if id_usuario <= 0:
            raise ValueError("O ID deve ser um número inteiro positivo.")

        nome_limpo = nome.strip()
        email_limpo = email.strip().lower()
        tipo_limpo = tipo.strip().lower()

        if not nome_limpo:
            raise ValueError("O nome não pode ficar vazio.")

        if not email_limpo:
            raise ValueError("O e-mail não pode ficar vazio.")

        if len(senha) < 5:
            raise ValueError("A senha deve ter no mínimo 5 caracteres.")

        if tipo_limpo not in TIPOS_VALIDOS:
            raise ValueError(f"Tipo inválido. Use: {', '.join(TIPOS_VALIDOS)}.")

        # Garante que o novo e-mail não pertence a outro usuário
        existente = self.repositorio.buscar_por_email(email_limpo)
        if existente is not None and existente.id != id_usuario:
            raise ValueError("Este e-mail já está em uso por outro usuário.")

        usuario = Usuarios(id=id_usuario, nome=nome_limpo, email=email_limpo, senha=senha, tipo=tipo_limpo)
        return self.repositorio.atualizar(usuario)

    def remover_usuario(self, id_usuario: int) -> bool:
        if id_usuario <= 0:
            raise ValueError("O ID deve ser um número inteiro positivo.")
        return self.repositorio.remover(id_usuario)
