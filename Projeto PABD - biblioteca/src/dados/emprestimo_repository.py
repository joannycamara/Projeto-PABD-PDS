from typing import Optional

import mysql.connector

from dominio.emprestimos import Emprestimos


class EmprestimosRepository:
    """Camada de dados: acesso ao banco para as tabelas emprestimos e reservas."""

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
                (id_usuario, id_livro, data_emprestimo, data_devolucao, renovado)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                emprestimo.id_usuario,
                emprestimo.id_livro,
                emprestimo.data_emprestimo,
                emprestimo.data_devolucao,
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
            SET id_usuario     = %s,
                id_livro       = %s,
                data_emprestimo = %s,
                data_devolucao  = %s,
                renovado        = %s
            WHERE id = %s
            """,
            (
                emprestimo.id_usuario,
                emprestimo.id_livro,
                emprestimo.data_emprestimo,
                emprestimo.data_devolucao,
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

        cursor.execute(
            """
            SELECT id, id_usuario, id_livro, data_emprestimo, data_devolucao, renovado
            FROM emprestimos
            ORDER BY id
            """
        )

        linhas = cursor.fetchall()
        cursor.close()

        return [self._mapear(linha) for linha in linhas]

    def buscar_por_id(self, id_emprestimo: int) -> Optional[Emprestimos]:
        cursor = self.conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, id_usuario, id_livro, data_emprestimo, data_devolucao, renovado
            FROM emprestimos
            WHERE id = %s
            """,
            (id_emprestimo,),
        )

        linha = cursor.fetchone()
        cursor.close()

        return self._mapear(linha) if linha else None

    def listar_por_usuario(self, id_usuario: int) -> list[Emprestimos]:
        """Retorna todo o histórico de um usuário. Usado em US11."""
        cursor = self.conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, id_usuario, id_livro, data_emprestimo, data_devolucao, renovado
            FROM emprestimos
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
            """
            SELECT
                e.id,
                e.id_usuario,
                e.id_livro,
                e.data_emprestimo,
                e.data_devolucao,
                e.renovado
            FROM emprestimos e
            WHERE e.id_usuario = %s
            AND e.data_devolucao IS NULL
            ORDER BY e.data_emprestimo DESC
            """,
            (id_usuario,),
        )


        linhas = cursor.fetchall()
        cursor.close()

        return [self._mapear(linha) for linha in linhas]

    def listar_atrasados(self, data_hoje: str) -> list[Emprestimos]:
        """Retorna empréstimos com data_devolucao vencida e sem devolução registrada.
        Usado em US06 (verificar pendência) e US15 (listar atrasados)."""
        cursor = self.conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT e.id, e.id_usuario, e.id_livro, e.data_emprestimo, e.data_devolucao, e.renovado
            FROM emprestimos e
            JOIN exemplares ex ON ex.id = e.id_livro
            WHERE e.data_devolucao < %s
              AND ex.disponivel = FALSE
            ORDER BY e.data_devolucao
            """,
            (data_hoje,),
        )

        linhas = cursor.fetchall()
        cursor.close()

        return [self._mapear(linha) for linha in linhas]

    def tem_emprestimo_ativo(self, id_livro: int) -> bool:
        """Verifica se o livro tem empréstimo ativo. Usado em US14."""
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) FROM emprestimos e
            JOIN exemplares ex ON ex.id = e.id_livro
            WHERE e.id_livro = %s AND ex.disponivel = FALSE
            """,
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
        )