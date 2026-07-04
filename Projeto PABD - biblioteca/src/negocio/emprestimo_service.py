from datetime import date, timedelta
from typing import Optional

from dados.emprestimo_repository import EmprestimosRepository
from dados.livro_repository import LivrosRepository
from dados.usuarios_repository import UsuariosRepository
from dominio.emprestimos import Emprestimos

PRAZO_EMPRESTIMO_DIAS = 14
PRAZO_RENOVACAO_DIAS = 7


class EmprestimoService:
    """Camada de negócio: regras de empréstimo, devolução, renovação e reserva
    (US05, US06, US07, US08, US09, US10, US11, US15)."""

    def __init__(
        self,
        repositorio_emprestimo: EmprestimosRepository,
        repositorio_livro: LivrosRepository,
        repositorio_usuario: UsuariosRepository,
    ) -> None:
        self.repositorio_emprestimo = repositorio_emprestimo
        self.repositorio_livro = repositorio_livro
        self.repositorio_usuario = repositorio_usuario

    # ------------------------------------------------------------------
    # US05 / US06 — Solicitar e Realizar Empréstimo
    # ------------------------------------------------------------------

    def realizar_emprestimo(self, id_usuario: int, id_livro: int) -> Emprestimos:
        """Registra um empréstimo. Pode ser chamado pelo aluno (US05) ou
        pelo bolsista (US06)."""

        usuario = self.repositorio_usuario.buscar_por_id(id_usuario)
        if usuario is None:
            raise ValueError("Aluno não encontrado. Verifique o dado informado.")

        livro = self.repositorio_livro.buscar_por_id(id_livro)
        if livro is None:
            raise ValueError("Livro não encontrado.")

        if not livro.disponivel:
            raise ValueError("Livro indisponível para empréstimo.")

        # US06: bloqueia aluno com empréstimo em atraso
        if self._usuario_tem_atraso(id_usuario):
            raise ValueError("Aluno com pendência. Regularize antes de realizar novo empréstimo.")

        hoje = date.today()
        data_devolucao = hoje + timedelta(days=PRAZO_EMPRESTIMO_DIAS)

        emprestimo = Emprestimos(
            id=None,
            id_usuario=id_usuario,
            id_livro=id_livro,
            data_emprestimo=str(hoje),
            data_devolucao=str(data_devolucao),
            renovado=False,
        )

        novo_id = self.repositorio_emprestimo.adicionar(emprestimo)
        emprestimo.id = novo_id

        # Marca livro como indisponível
        livro.disponivel = False
        self.repositorio_livro.atualizar(livro)

        return emprestimo

    # ------------------------------------------------------------------
    # US07 — Renovar Empréstimo (bolsista)
    # ------------------------------------------------------------------

    def renovar_emprestimo(self, id_emprestimo: int) -> Emprestimos:
        emprestimo = self.repositorio_emprestimo.buscar_por_id(id_emprestimo)
        if emprestimo is None:
            raise ValueError("Empréstimo não encontrado.")

        hoje = date.today()
        data_devolucao = date.fromisoformat(emprestimo.data_devolucao)

        if hoje > data_devolucao:
            raise ValueError("Não é possível renovar. O prazo já foi ultrapassado.")

        # US10: bloqueia renovação se houver reserva ativa para o livro
        if self._livro_tem_reserva(emprestimo.id_livro):
            raise ValueError("Renovação não permitida. O livro possui reserva.")

        nova_devolucao = data_devolucao + timedelta(days=PRAZO_RENOVACAO_DIAS)
        emprestimo.data_devolucao = str(nova_devolucao)
        emprestimo.renovado = True

        self.repositorio_emprestimo.atualizar(emprestimo)
        return emprestimo

    # ------------------------------------------------------------------
    # US08 — Registrar Devolução (bolsista)
    # ------------------------------------------------------------------

    def registrar_devolucao(self, id_emprestimo: int) -> dict:
        """Registra a devolução e retorna um dict com os dados do resultado,
        incluindo se houve atraso e quantos dias."""

        emprestimo = self.repositorio_emprestimo.buscar_por_id(id_emprestimo)
        if emprestimo is None:
            raise ValueError("Nenhum empréstimo ativo encontrado para os dados informados.")

        hoje = date.today()
        data_devolucao_prevista = date.fromisoformat(emprestimo.data_devolucao)
        dias_atraso = (hoje - data_devolucao_prevista).days

        # Registra a devolução (usa data_devolucao como data real de devolução)
        emprestimo.data_devolucao = str(hoje)
        self.repositorio_emprestimo.atualizar(emprestimo)

        # Libera o livro
        livro = self.repositorio_livro.buscar_por_id(emprestimo.id_livro)
        if livro:
            livro.disponivel = True
            self.repositorio_livro.atualizar(livro)

        return {
            "emprestimo": emprestimo,
            "dias_atraso": max(dias_atraso, 0),
            "atrasado": dias_atraso > 0,
        }

    def buscar_emprestimos_ativos_por_usuario(self, id_usuario: int) -> list[Emprestimos]:
        """Busca empréstimos ainda não devolvidos de um usuário. Usado em US08."""
        return self.repositorio_emprestimo.listar_ativos_por_usuario(id_usuario)

    # ------------------------------------------------------------------
    # US10 — Reservar Livro (aluno)
    # ------------------------------------------------------------------

    def reservar_livro(self, id_usuario: int, id_livro: int) -> dict:
        livro = self.repositorio_livro.buscar_por_id(id_livro)
        if livro is None:
            raise ValueError("Livro não encontrado.")

        if livro.disponivel:
            raise ValueError("O livro está disponível. Realize o empréstimo diretamente.")

        if self._usuario_tem_reserva_para_livro(id_usuario, id_livro):
            raise ValueError("Você já possui uma reserva ativa para este livro.")

        reserva = self.repositorio_emprestimo.adicionar_reserva(id_usuario, id_livro)
        posicao = self.repositorio_emprestimo.posicao_na_fila(id_livro, reserva["id"])

        return {
            "reserva": reserva,
            "posicao_fila": posicao,
        }

    # ------------------------------------------------------------------
    # US11 — Histórico de Empréstimos
    # ------------------------------------------------------------------

    def historico_por_usuario(self, id_usuario: int) -> list[Emprestimos]:
        if id_usuario <= 0:
            raise ValueError("O ID deve ser um número inteiro positivo.")
        return self.repositorio_emprestimo.listar_por_usuario(id_usuario)

    # ------------------------------------------------------------------
    # US15 — Livros Atrasados (bibliotecário)
    # ------------------------------------------------------------------

    def listar_emprestimos_atrasados(self) -> list[dict]:
        """Retorna lista de dicts com empréstimo + dados do usuário + dias de atraso."""
        hoje = str(date.today())
        emprestimos_atrasados = self.repositorio_emprestimo.listar_atrasados(hoje)

        resultado = []
        for emp in emprestimos_atrasados:
            usuario = self.repositorio_usuario.buscar_por_id(emp.id_usuario)
            dias_atraso = (date.today() - date.fromisoformat(emp.data_devolucao)).days
            resultado.append({
                "emprestimo": emp,
                "usuario": usuario,
                "dias_atraso": dias_atraso,
            })

        return resultado

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _usuario_tem_atraso(self, id_usuario: int) -> bool:
        hoje = str(date.today())
        atrasados = self.repositorio_emprestimo.listar_atrasados(hoje)
        return any(e.id_usuario == id_usuario for e in atrasados)

    def _livro_tem_reserva(self, id_livro: int) -> bool:
        return self.repositorio_emprestimo.tem_reserva_ativa(id_livro)

    def _usuario_tem_reserva_para_livro(self, id_usuario: int, id_livro: int) -> bool:
        return self.repositorio_emprestimo.tem_reserva_ativa_por_usuario(id_usuario, id_livro)

    # ------------------------------------------------------------------
    # Suporte ao LivroService (US14)
    # ------------------------------------------------------------------

    def livro_tem_emprestimo_ativo(self, id_livro: int) -> bool:
        return self.repositorio_emprestimo.tem_emprestimo_ativo(id_livro)

    def livro_tem_reserva_ativa(self, id_livro: int) -> bool:
        return self._livro_tem_reserva(id_livro)