from typing import Optional

import mysql.connector

from src.dominio.livro import Livros


class LivrosRepository:
    """Camada data: faz o acesso ao banco e executa SQL."""

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao

    def adicionar(self, livros: Livros) -> int:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO livros
            (titulo, autor, genero, disponivel)
            VALUES (%s, %s, %s, %s)
            """,
            (
                livros.titulo,
                livros.autor,
                livros.genero,
                livros.disponivel,
            ),
        )

        self.conexao.commit()

        novo_id = int(cursor.lastrowid)

        cursor.close()

        return novo_id

    def listar_todos(self) -> list[Livros]:

        cursor = self.conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                titulo,
                autor,
                genero,
                disponivel
            FROM livros
            ORDER BY id
            """
        )

        linhas = cursor.fetchall()

        cursor.close()

        return [
            Livros(
                id=linha["id"],
                titulo=linha["titulo"],
                autor=linha["autor"],
                genero=linha["genero"],
                disponivel=bool(linha["disponivel"]),
            )
            for linha in linhas
        ]

    def buscar_por_id(self, id_livros: int) -> Optional[Livros]:

        cursor = self.conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                titulo,
                autor,
                genero,
                disponivel
            FROM livros
            WHERE id = %s
            """,
            (id_livros,),
        )

        linha = cursor.fetchone()

        cursor.close()

        if linha is None:
            return None

        return Livros(
            id=linha["id"],
            titulo=linha["titulo"],
            autor=linha["autor"],
            genero=linha["genero"],
            disponivel=bool(linha["disponivel"]),
        )

    def atualizar(self, livros: Livros) -> bool:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE livros
            SET
                titulo = %s,
                autor = %s,
                genero = %s,
                disponivel = %s
            WHERE id = %s
            """,
            (
                livros.titulo,
                livros.autor,
                livros.genero,
                livros.disponivel,
                livros.id,
            ),
        )

        self.conexao.commit()

        afetados = cursor.rowcount > 0

        cursor.close()

        return afetados

    def remover(self, id_livros: int) -> bool:

        cursor = self.conexao.cursor()

        cursor.execute(
            "DELETE FROM livros WHERE id = %s",
            (id_livros,),
        )

        self.conexao.commit()

        afetados = cursor.rowcount > 0

        cursor.close()

        return afetados