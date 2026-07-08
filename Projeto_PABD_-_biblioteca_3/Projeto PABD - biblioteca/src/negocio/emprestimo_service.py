from datetime import date, timedelta
from typing import Optional

from dados.emprestimo_repository import EmprestimosRepository
from dados.livro_repository import LivrosRepository
from dados.usuarios_repository import UsuariosRepository
from dominio.emprestimos import Emprestimos
from dominio.reserva import Reserva
from dominio.solicitacao import SolicitacaoEmprestimo

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

        if self.repositorio_emprestimo.listar_ativos_por_usuario(id_usuario):
            raise ValueError("Este aluno já possui um empréstimo ativo. Devolva-o antes de solicitar outro.")

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
            data_devolucao_real=None,
        )

        novo_id = self.repositorio_emprestimo.adicionar(emprestimo)
        emprestimo.id = novo_id

        # Marca livro como indisponível
        livro.disponivel = False
        self.repositorio_livro.atualizar(livro)

        return emprestimo

    # ------------------------------------------------------------------
    # US05 — Solicitar Empréstimo (aluno) / Aprovar ou Rejeitar (bolsista)
    # ------------------------------------------------------------------

    def solicitar_emprestimo(self, id_usuario: int, id_livro: int) -> SolicitacaoEmprestimo:
        """O aluno não empresta o livro diretamente: ele cria uma solicitação
        pendente, que o bolsista aprova (US06) ou rejeita."""
        usuario = self.repositorio_usuario.buscar_por_id(id_usuario)
        if usuario is None:
            raise ValueError("Aluno não encontrado. Verifique o dado informado.")

        livro = self.repositorio_livro.buscar_por_id(id_livro)
        if livro is None:
            raise ValueError("Livro não encontrado.")

        if not livro.disponivel:
            raise ValueError("Livro indisponível para empréstimo.")

        if self.repositorio_emprestimo.listar_ativos_por_usuario(id_usuario):
            raise ValueError("Você já possui um empréstimo ativo. Devolva-o antes de solicitar outro.")

        if self.repositorio_emprestimo.tem_solicitacao_pendente(id_usuario):
            raise ValueError("Você já tem uma solicitação de empréstimo pendente de aprovação.")

        if self._usuario_tem_atraso(id_usuario):
            raise ValueError("Você tem uma pendência em atraso. Regularize antes de solicitar outro empréstimo.")

        novo_id = self.repositorio_emprestimo.adicionar_solicitacao(id_usuario, id_livro)
        return SolicitacaoEmprestimo(
            id=novo_id, id_usuario=id_usuario, id_livro=id_livro,
            data_solicitacao=str(date.today()), status="pendente",
        )

    def listar_solicitacoes_pendentes(self) -> list[SolicitacaoEmprestimo]:
        """Usado pelo bolsista para ver os pedidos aguardando aprovação."""
        return self.repositorio_emprestimo.listar_solicitacoes_pendentes()

    def listar_solicitacoes_do_usuario(self, id_usuario: int) -> list[SolicitacaoEmprestimo]:
        """Usado na tela do aluno, para acompanhar o status dos próprios pedidos."""
        return self.repositorio_emprestimo.listar_solicitacoes_por_usuario(id_usuario)

    def aprovar_solicitacao(self, id_solicitacao: int) -> Emprestimos:
        """O bolsista aprova a solicitação: ela vira um empréstimo de verdade."""
        solicitacao = self.repositorio_emprestimo.buscar_solicitacao_por_id(id_solicitacao)
        if solicitacao is None:
            raise ValueError("Solicitação não encontrada.")

        if not solicitacao.pendente:
            raise ValueError("Esta solicitação já foi analisada.")

        emprestimo = self.realizar_emprestimo(solicitacao.id_usuario, solicitacao.id_livro)
        self.repositorio_emprestimo.atualizar_status_solicitacao(id_solicitacao, "aprovada")
        return emprestimo

    def rejeitar_solicitacao(self, id_solicitacao: int) -> bool:
        """O bolsista rejeita a solicitação (o livro segue disponível)."""
        solicitacao = self.repositorio_emprestimo.buscar_solicitacao_por_id(id_solicitacao)
        if solicitacao is None:
            raise ValueError("Solicitação não encontrada.")

        if not solicitacao.pendente:
            raise ValueError("Esta solicitação já foi analisada.")

        return self.repositorio_emprestimo.atualizar_status_solicitacao(id_solicitacao, "rejeitada")

    def renovar_emprestimo(self, id_emprestimo: int) -> Emprestimos:
        emprestimo = self.repositorio_emprestimo.buscar_por_id(id_emprestimo)
        if emprestimo is None:
            raise ValueError("Empréstimo não encontrado.")

        if not emprestimo.ativo:
            raise ValueError("Este empréstimo já foi devolvido.")

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

        # Registra a devolução real, preservando o prazo original em data_devolucao
        emprestimo.data_devolucao_real = str(hoje)
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

    def emprestimo_atual_do_usuario(self, id_usuario: int) -> Optional[Emprestimos]:
        """Retorna o empréstimo ativo mais recente do usuário, ou None se não houver.
        Usado nas telas de Aluno e Bolsista para destacar 'o empréstimo atual'."""
        ativos = self.repositorio_emprestimo.listar_ativos_por_usuario(id_usuario)
        return ativos[0] if ativos else None

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

    def listar_reservas_ativas(self) -> list[Reserva]:
        """Lista todas as reservas pendentes do sistema. Usado pelo bolsista
        para saber quais alunos estão esperando por um livro."""
        return self.repositorio_emprestimo.listar_reservas_ativas()

    def listar_reservas_do_usuario(self, id_usuario: int) -> list[Reserva]:
        """Lista as reservas de um usuário. Usado na tela do aluno."""
        return self.repositorio_emprestimo.listar_reservas_por_usuario(id_usuario)

    def posicao_na_fila(self, id_livro: int, id_reserva: int) -> int:
        return self.repositorio_emprestimo.posicao_na_fila(id_livro, id_reserva)

    def criar_emprestimo_a_partir_da_reserva(self, id_reserva: int) -> Emprestimos:
        """Converte uma reserva ativa em empréstimo (usado pelo bolsista quando
        o livro reservado fica disponível). Ao concluir, a reserva é encerrada."""
        reserva = self.repositorio_emprestimo.buscar_reserva_por_id(id_reserva)
        if reserva is None or not reserva.ativa:
            raise ValueError("Reserva não encontrada ou já atendida.")

        livro = self.repositorio_livro.buscar_por_id(reserva.id_livro)
        if livro is None:
            raise ValueError("Livro não encontrado.")

        if not livro.disponivel:
            raise ValueError("Este livro ainda não está disponível para empréstimo.")

        emprestimo = self.realizar_emprestimo(reserva.id_usuario, reserva.id_livro)
        self.repositorio_emprestimo.cancelar_reserva(id_reserva)
        return emprestimo

    # ------------------------------------------------------------------
    # US11 — Histórico de Empréstimos
    # ------------------------------------------------------------------

    def historico_por_usuario(self, id_usuario: int) -> list[Emprestimos]:
        if id_usuario <= 0:
            raise ValueError("O ID deve ser um número inteiro positivo.")
        return self.repositorio_emprestimo.listar_por_usuario(id_usuario)

    def listar_todos(self) -> list[Emprestimos]:
        """Lista todos os empréstimos já registrados no sistema (ativos, atrasados
        e devolvidos). Usado na aba 'Meus Registros' do bolsista."""
        return self.repositorio_emprestimo.listar_todos()

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