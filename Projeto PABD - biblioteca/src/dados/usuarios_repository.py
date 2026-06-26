from typing import Optional

import mysql.connector

from dominio.usuarios import Usuarios


class UsuariosRepository:
    """Camada de dados: acesso ao banco para a tabela usuarios."""

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao

    # ------------------------------------------------------------------
    # Escrita
    # ------------------------------------------------------------------

    def adicionar(self, usuarios: Usuarios) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO usuarios (nome, email, senha, tipo)
            VALUES (%s, %s, %s, %s)
            """,
            (usuarios.nome, usuarios.email, usuarios.senha, usuarios.tipo),
        )

        self.conexao.commit()
        novo_id = int(cursor.lastrowid)
        cursor.close()
        return novo_id

    def atualizar(self, usuarios: Usuarios) -> bool:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE usuarios
            SET nome = %s, email = %s, senha = %s, tipo = %s
            WHERE id = %s
            """,
            (usuarios.nome, usuarios.email, usuarios.senha, usuarios.tipo, usuarios.id),
        )

        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados

    def remover(self, id_usuario: int) -> bool:
        cursor = self.conexao.cursor()

        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id_usuario,))

        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------

    def listar_todos(self) -> list[Usuarios]:
        cursor = self.conexao.cursor(dictionary=True)

        cursor.execute("SELECT id, nome, email, senha, tipo FROM usuarios ORDER BY id")

        linhas = cursor.fetchall()
        cursor.close()

        return [self._mapear(linha) for linha in linhas]

    def buscar_por_id(self, id_usuario: int) -> Optional[Usuarios]:
        cursor = self.conexao.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, nome, email, senha, tipo FROM usuarios WHERE id = %s",
            (id_usuario,),
        )

        linha = cursor.fetchone()
        cursor.close()

        return self._mapear(linha) if linha else None

    def buscar_por_email(self, email: str) -> Optional[Usuarios]:
        """Usado em US01 (verificar duplicidade) e US02 (login)."""
        cursor = self.conexao.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, nome, email, senha, tipo FROM usuarios WHERE email = %s",
            (email,),
        )

        linha = cursor.fetchone()
        cursor.close()

        return self._mapear(linha) if linha else None

    def buscar_por_nome(self, nome: str) -> list[Usuarios]:
        """Busca parcial por nome. Usado em US11 (bibliotecário busca histórico por nome)."""
        cursor = self.conexao.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, nome, email, senha, tipo FROM usuarios WHERE nome LIKE %s ORDER BY nome",
            (f"%{nome}%",),
        )

        linhas = cursor.fetchall()
        cursor.close()

        return [self._mapear(linha) for linha in linhas]

    # ------------------------------------------------------------------
    # Mapeamento interno
    # ------------------------------------------------------------------

    @staticmethod
    def _mapear(linha: dict) -> Usuarios:
        return Usuarios(
            id=linha["id"],
            nome=linha["nome"],
            email=linha["email"],
            senha=linha["senha"],
            tipo=linha["tipo"],
        )