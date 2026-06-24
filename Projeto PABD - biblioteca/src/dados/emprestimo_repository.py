from typing import Optional
from datetime import date

import mysql.connector

from src.dominio.emprestimos import Emprestimos


class EmprestimosRepository:
    """Camada data: faz o acesso ao banco e executa SQL."""

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao

    def adicionar(self, emprestimos: Emprestimos) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO emprestimos
            (id_usuario, id_livro, data_emprestimo, data_devolucao, renovado)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                emprestimos.id_usuario,
                emprestimos.id_livro,
                emprestimos.data_emprestimo,
                emprestimos.data_devolucao,
                emprestimos.renovado,
            ),
        )

        self.conexao.commit()

        novo_id = int(cursor.lastrowid)

        cursor.close()

        return novo_id

    def listar_todos(self) -> list[Emprestimos]:

        cursor = self.conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                id_usuario,
                id_livro,
                data_emprestimo,
                data_devolucao,
                renovado
            FROM emprestimos
            ORDER BY id
            """
        )

        linhas = cursor.fetchall()

        cursor.close()

        return [
            Emprestimos(
                id=linha["id"],
                id_usuario=linha["id_usuario"],
                id_livro=linha["id_livro"],
                data_emprestimo=linha["data_emprestimo"],
                data_devolucao=linha["data_devolucao"],
                renovado=bool(linha["renovado"]),
            )
            for linha in linhas
        ]

    def buscar_por_id(self, id_emprestimos: int) -> Optional[Emprestimos]:

        cursor = self.conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                id_usuario,
                id_livro,
                data_emprestimo,
                data_devolucao,
                renovado
            FROM emprestimos
            WHERE id = %s
            """,
            (id_emprestimos,),
        )

        linha = cursor.fetchone()

        cursor.close()

        if linha is None:
            return None

        return Emprestimos(
            id=linha["id"],
            id_usuario=linha["id_usuario"],
            id_livro=linha["id_livro"],
            data_emprestimo=linha["data_emprestimo"],
            data_devolucao=linha["data_devolucao"],
            renovado=bool(linha["renovado"]),
        )

    def atualizar(self, emprestimos: Emprestimos) -> bool:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE emprestimos
            SET
                id_usuario = %s,
                id_livro = %s,
                data_emprestimo = %s,
                data_devolucao = %s,
                renovado = %s
            WHERE id = %s
            """,
            (
                emprestimos.id_usuario,
                emprestimos.id_livro,
                emprestimos.data_emprestimo,
                emprestimos.data_devolucao,
                emprestimos.renovado,
                emprestimos.id,
            ),
        )

        self.conexao.commit()

        afetados = cursor.rowcount > 0

        cursor.close()

        return afetados

    def remover(self, id_emprestimos: int) -> bool:

        cursor = self.conexao.cursor()

        cursor.execute(
            "DELETE FROM emprestimos WHERE id = %s",
            (id_emprestimos,),
        )

        self.conexao.commit()

        afetados = cursor.rowcount > 0

        cursor.close()

        return afetados