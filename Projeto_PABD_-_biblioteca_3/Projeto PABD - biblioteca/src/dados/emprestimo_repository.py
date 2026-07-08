from typing import Optional

import mysql.connector

from dominio.emprestimos import Emprestimos
from dominio.reserva import Reserva
from dominio.solicitacao import SolicitacaoEmprestimo


class EmprestimosRepository:
    """Camada de dados: acesso ao banco para as tabelas emprestimos e reservas."""

    _COLUNAS = "id, id_usuario, id_livro, data_emprestimo, data_devolucao, data_devolucao_real, renovado"

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao

    # ------------------------------------------------------------------
    # Empréstimos — Escrita
    # ------------------------------------------------------------------

    def adicionar(self, emprestimo: Emprestimos) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO emprestimos
                (id_usuario, id_livro, data_emprestimo, data_devolucao, data_devolucao_real, renovado)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                emprestimo.id_usuario,
                emprestimo.id_livro,
                emprestimo.data_emprestimo,
                emprestimo.data_devolucao,
                emprestimo.data_devolucao_real,
                emprestimo.renovado,
            ),
        )

        self.conexao.commit()
        novo_id = int(cursor.lastrowid)
        cursor.close()
        return novo_id

    def atualizar(self, emprestimo: Emprestimos) -> bool:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE emprestimos
            SET id_usuario          = %s,
                id_livro            = %s,
                data_emprestimo     = %s,
                data_devolucao      = %s,
                data_devolucao_real = %s,
                renovado            = %s
            WHERE id = %s
            """,
            (
                emprestimo.id_usuario,
                emprestimo.id_livro,
                emprestimo.data_emprestimo,
                emprestimo.data_devolucao,
                emprestimo.data_devolucao_real,
                emprestimo.renovado,
                emprestimo.id,
            ),
        )

        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados

    def remover(self, id_emprestimo: int) -> bool:
        cursor = self.conexao.cursor()

        cursor.execute("DELETE FROM emprestimos WHERE id = %s", (id_emprestimo,))

        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados

    # ------------------------------------------------------------------
    # Empréstimos — Leitura
    # ------------------------------------------------------------------

    def listar_todos(self) -> list[Emprestimos]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(f"SELECT {self._COLUNAS} FROM emprestimos ORDER BY id")
        linhas = cursor.fetchall()
        cursor.close()
        return [self._mapear(linha) for linha in linhas]

    def buscar_por_id(self, id_emprestimo: int) -> Optional[Emprestimos]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(f"SELECT {self._COLUNAS} FROM emprestimos WHERE id = %s", (id_emprestimo,))
        linha = cursor.fetchone()
        cursor.close()
        return self._mapear(linha) if linha else None

    def listar_por_usuario(self, id_usuario: int) -> list[Emprestimos]:
        """Retorna todo o histórico de um usuário (ativos + já devolvidos). Usado em US11."""
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            f"""
            SELECT {self._COLUNAS} FROM emprestimos
            WHERE id_usuario = %s
            ORDER BY data_emprestimo DESC
            """,
            (id_usuario,),
        )
        linhas = cursor.fetchall()
        cursor.close()
        return [self._mapear(linha) for linha in linhas]

    def listar_ativos_por_usuario(self, id_usuario: int) -> list[Emprestimos]:
        """Retorna empréstimos ainda não devolvidos de um usuário. Usado em US08."""
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            f"""
            SELECT {self._COLUNAS} FROM emprestimos
            WHERE id_usuario = %s
              AND data_devolucao_real IS NULL
            ORDER BY data_emprestimo DESC
            """,
            (id_usuario,),
        )
        linhas = cursor.fetchall()
        cursor.close()
        return [self._mapear(linha) for linha in linhas]

    def listar_atrasados(self, data_hoje: str) -> list[Emprestimos]:
        """Retorna empréstimos ainda não devolvidos com prazo vencido.
        Usado em US06 (verificar pendência) e US15 (listar atrasados)."""
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            f"""
            SELECT {self._COLUNAS} FROM emprestimos
            WHERE data_devolucao_real IS NULL
              AND data_devolucao < %s
            ORDER BY data_devolucao
            """,
            (data_hoje,),
        )
        linhas = cursor.fetchall()
        cursor.close()
        return [self._mapear(linha) for linha in linhas]

    def tem_emprestimo_ativo(self, id_livro: int) -> bool:
        """Verifica se o livro (exemplar) tem empréstimo ativo. Usado em US14."""
        cursor = self.conexao.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM emprestimos WHERE id_livro = %s AND data_devolucao_real IS NULL",
            (id_livro,),
        )
        (total,) = cursor.fetchone()
        cursor.close()
        return total > 0

    # ------------------------------------------------------------------
    # Reservas — Escrita
    # ------------------------------------------------------------------

    def adicionar_reserva(self, id_usuario: int, id_livro: int) -> dict:
        """Registra uma reserva na tabela reservas. Usado em US10."""
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO reservas (id_usuario, id_livro, data_reserva, ativa)
            VALUES (%s, %s, CURDATE(), TRUE)
            """,
            (id_usuario, id_livro),
        )

        self.conexao.commit()
        novo_id = int(cursor.lastrowid)
        cursor.close()

        return {"id": novo_id, "id_usuario": id_usuario, "id_livro": id_livro}

    def cancelar_reserva(self, id_reserva: int) -> bool:
        cursor = self.conexao.cursor()

        cursor.execute(
            "UPDATE reservas SET ativa = FALSE WHERE id = %s",
            (id_reserva,),
        )

        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados

    # ------------------------------------------------------------------
    # Reservas — Leitura
    # ------------------------------------------------------------------

    def tem_reserva_ativa(self, id_livro: int) -> bool:
        """Verifica se o livro tem reserva ativa. Usado em US07 e US14."""
        cursor = self.conexao.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM reservas WHERE id_livro = %s AND ativa = TRUE",
            (id_livro,),
        )

        (total,) = cursor.fetchone()
        cursor.close()

        return total > 0

    def tem_reserva_ativa_por_usuario(self, id_usuario: int, id_livro: int) -> bool:
        """Verifica se o usuário já reservou este livro. Usado em US10."""
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) FROM reservas
            WHERE id_usuario = %s AND id_livro = %s AND ativa = TRUE
            """,
            (id_usuario, id_livro),
        )

        (total,) = cursor.fetchone()
        cursor.close()

        return total > 0

    def posicao_na_fila(self, id_livro: int, id_reserva: int) -> int:
        """Retorna a posição da reserva na fila do livro. Usado em US10."""
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) FROM reservas
            WHERE id_livro = %s AND ativa = TRUE AND id <= %s
            """,
            (id_livro, id_reserva),
        )

        (posicao,) = cursor.fetchone()
        cursor.close()

        return int(posicao)

    def listar_reservas_ativas(self) -> list[Reserva]:
        """Lista todas as reservas pendentes do sistema. Usado pelo bolsista."""
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, id_usuario, id_livro, data_reserva, ativa FROM reservas "
            "WHERE ativa = TRUE ORDER BY data_reserva"
        )
        linhas = cursor.fetchall()
        cursor.close()
        return [self._mapear_reserva(linha) for linha in linhas]

    def listar_reservas_por_usuario(self, id_usuario: int) -> list[Reserva]:
        """Lista as reservas (ativas e antigas) de um usuário. Usado em US10."""
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, id_usuario, id_livro, data_reserva, ativa FROM reservas "
            "WHERE id_usuario = %s ORDER BY data_reserva DESC",
            (id_usuario,),
        )
        linhas = cursor.fetchall()
        cursor.close()
        return [self._mapear_reserva(linha) for linha in linhas]

    def buscar_reserva_por_id(self, id_reserva: int) -> Optional[Reserva]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, id_usuario, id_livro, data_reserva, ativa FROM reservas WHERE id = %s",
            (id_reserva,),
        )
        linha = cursor.fetchone()
        cursor.close()
        return self._mapear_reserva(linha) if linha else None

    # ------------------------------------------------------------------
    # Solicitações de Empréstimo — Escrita
    # ------------------------------------------------------------------

    def adicionar_solicitacao(self, id_usuario: int, id_livro: int) -> int:
        cursor = self.conexao.cursor()
        cursor.execute(
            """
            INSERT INTO solicitacoes_emprestimo (id_usuario, id_livro, data_solicitacao, status)
            VALUES (%s, %s, CURDATE(), 'pendente')
            """,
            (id_usuario, id_livro),
        )
        self.conexao.commit()
        novo_id = int(cursor.lastrowid)
        cursor.close()
        return novo_id

    def atualizar_status_solicitacao(self, id_solicitacao: int, status: str) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "UPDATE solicitacoes_emprestimo SET status = %s WHERE id = %s",
            (status, id_solicitacao),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados

    # ------------------------------------------------------------------
    # Solicitações de Empréstimo — Leitura
    # ------------------------------------------------------------------

    _COLUNAS_SOLICITACAO = "id, id_usuario, id_livro, data_solicitacao, status"

    def buscar_solicitacao_por_id(self, id_solicitacao: int) -> Optional[SolicitacaoEmprestimo]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            f"SELECT {self._COLUNAS_SOLICITACAO} FROM solicitacoes_emprestimo WHERE id = %s",
            (id_solicitacao,),
        )
        linha = cursor.fetchone()
        cursor.close()
        return self._mapear_solicitacao(linha) if linha else None

    def listar_solicitacoes_pendentes(self) -> list[SolicitacaoEmprestimo]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            f"SELECT {self._COLUNAS_SOLICITACAO} FROM solicitacoes_emprestimo "
            "WHERE status = 'pendente' ORDER BY data_solicitacao"
        )
        linhas = cursor.fetchall()
        cursor.close()
        return [self._mapear_solicitacao(linha) for linha in linhas]

    def listar_solicitacoes_por_usuario(self, id_usuario: int) -> list[SolicitacaoEmprestimo]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            f"SELECT {self._COLUNAS_SOLICITACAO} FROM solicitacoes_emprestimo "
            "WHERE id_usuario = %s ORDER BY data_solicitacao DESC",
            (id_usuario,),
        )
        linhas = cursor.fetchall()
        cursor.close()
        return [self._mapear_solicitacao(linha) for linha in linhas]

    def tem_solicitacao_pendente(self, id_usuario: int) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM solicitacoes_emprestimo WHERE id_usuario = %s AND status = 'pendente'",
            (id_usuario,),
        )
        (total,) = cursor.fetchone()
        cursor.close()
        return total > 0

    # ------------------------------------------------------------------
    # Mapeamento interno
    # ------------------------------------------------------------------

    @staticmethod
    def _mapear(linha: dict) -> Emprestimos:
        return Emprestimos(
            id=linha["id"],
            id_usuario=linha["id_usuario"],
            id_livro=linha["id_livro"],
            data_emprestimo=str(linha["data_emprestimo"]),
            data_devolucao=str(linha["data_devolucao"]),
            renovado=bool(linha["renovado"]),
            data_devolucao_real=(str(linha["data_devolucao_real"]) if linha["data_devolucao_real"] else None),
        )

    @staticmethod
    def _mapear_reserva(linha: dict) -> Reserva:
        return Reserva(
            id=linha["id"],
            id_usuario=linha["id_usuario"],
            id_livro=linha["id_livro"],
            data_reserva=str(linha["data_reserva"]),
            ativa=bool(linha["ativa"]),
        )

    @staticmethod
    def _mapear_solicitacao(linha: dict) -> SolicitacaoEmprestimo:
        return SolicitacaoEmprestimo(
            id=linha["id"],
            id_usuario=linha["id_usuario"],
            id_livro=linha["id_livro"],
            data_solicitacao=str(linha["data_solicitacao"]),
            status=linha["status"],
        )
