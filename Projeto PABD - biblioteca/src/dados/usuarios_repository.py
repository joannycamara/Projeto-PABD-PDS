from typing import Optional

import mysql.connector

from src.dominio.usuarios import Usuarios


class UsuariosRepository:
    """Camada data: faz o acesso ao banco e executa SQL."""

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao

    def adicionar(self, usuarios: Usuarios) -> int:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO usuarios
            (nome, senha, tipo)
            VALUES (%s, %s, %s)
            """,
            (
                usuarios.nome,
                usuarios.senha,
                usuarios.tipo,
            ),
        )

        self.conexao.commit()

        novo_id = int(cursor.lastrowid)

        cursor.close()

        return novo_id

    def listar_todos(self) -> list[Usuarios]:

        cursor = self.conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                nome,
                senha,
                tipo
            FROM usuarios
            ORDER BY id
            """
        )

        linhas = cursor.fetchall()

        cursor.close()

        return [
            Usuarios(
                id=linha["id"],
                nome=linha["nome"],
                senha=linha["senha"],
                tipo=linha["tipo"],
            )
            for linha in linhas
        ]

    def buscar_por_id(self, id_usuarios: int) -> Optional[Usuarios]:

        cursor = self.conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                nome,
                senha,
                tipo
            FROM usuarios
            WHERE id = %s
            """,
            (id_usuarios,),
        )

        linha = cursor.fetchone()

        cursor.close()

        if linha is None:
            return None

        return Usuarios(
            id=linha["id"],
            nome=linha["nome"],
            senha=linha["senha"],
            tipo=linha["tipo"],
        )

    def atualizar(self, usuarios: Usuarios) -> bool:

        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE usuarios
            SET
                nome = %s,
                senha = %s,
                tipo = %s
            WHERE id = %s
            """,
            (
                usuarios.nome,
                usuarios.senha,
                usuarios.tipo,
                usuarios.id,
            ),
        )

        self.conexao.commit()

        afetados = cursor.rowcount > 0

        cursor.close()

        return afetados

    def remover(self, id_usuarios: int) -> bool:

        cursor = self.conexao.cursor()

        cursor.execute(
            "DELETE FROM usuarios WHERE id = %s",
            (id_usuarios,),
        )

        self.conexao.commit()

        afetados = cursor.rowcount > 0

        cursor.close()

        return afetados