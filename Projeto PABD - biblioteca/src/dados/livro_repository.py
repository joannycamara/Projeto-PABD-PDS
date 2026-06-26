from typing import Optional

import mysql.connector

from dominio.livro import Livros


class LivrosRepository:
    """Camada de dados: acesso ao banco para a tabela livros."""

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao

    # ------------------------------------------------------------------
    # Escrita
    # ------------------------------------------------------------------

    def adicionar(self, livro: Livros) -> int:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            INSERT INTO livros (titulo, autor, genero, isbn, disponivel)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (livro.titulo, livro.autor, livro.genero, livro.isbn, livro.disponivel),
        )

        self.conexao.commit()
        novo_id = int(cursor.lastrowid)
        cursor.close()
        return novo_id

    def atualizar(self, livro: Livros) -> bool:
        cursor = self.conexao.cursor()

        cursor.execute(
            """
            UPDATE livros
            SET titulo = %s, autor = %s, genero = %s, isbn = %s, disponivel = %s
            WHERE id = %s
            """,
            (livro.titulo, livro.autor, livro.genero, livro.isbn, livro.disponivel, livro.id),
        )

        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados

    def remover(self, id_livro: int) -> bool:
        cursor = self.conexao.cursor()

        cursor.execute("DELETE FROM livros WHERE id = %s", (id_livro,))

        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------

    def listar_todos(self) -> list[Livros]:
        cursor = self.conexao.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, titulo, autor, genero, isbn, disponivel FROM livros ORDER BY titulo"
        )

        linhas = cursor.fetchall()
        cursor.close()

        return [self._mapear(linha) for linha in linhas]

    def listar_por_disponibilidade(self, disponivel: bool) -> list[Livros]:
        """Retorna livros filtrados por disponibilidade. Usado em US09."""
        cursor = self.conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, titulo, autor, genero, isbn, disponivel
            FROM livros
            WHERE disponivel = %s
            ORDER BY titulo
            """,
            (disponivel,),
        )

        linhas = cursor.fetchall()
        cursor.close()

        return [self._mapear(linha) for linha in linhas]

    def buscar_por_id(self, id_livro: int) -> Optional[Livros]:
        cursor = self.conexao.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, titulo, autor, genero, isbn, disponivel FROM livros WHERE id = %s",
            (id_livro,),
        )

        linha = cursor.fetchone()
        cursor.close()

        return self._mapear(linha) if linha else None

    def buscar_por_isbn(self, isbn: str) -> Optional[Livros]:
        """Usado em US12 (evitar ISBN duplicado) e US13 (validar edição)."""
        cursor = self.conexao.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, titulo, autor, genero, isbn, disponivel FROM livros WHERE isbn = %s",
            (isbn,),
        )

        linha = cursor.fetchone()
        cursor.close()

        return self._mapear(linha) if linha else None

    def buscar_por_titulo_ou_autor(self, termo: str) -> list[Livros]:
        """Busca parcial por título ou autor. Usado em US04."""
        cursor = self.conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, titulo, autor, genero, isbn, disponivel
            FROM livros
            WHERE titulo LIKE %s OR autor LIKE %s
            ORDER BY titulo
            """,
            (f"%{termo}%", f"%{termo}%"),
        )

        linhas = cursor.fetchall()
        cursor.close()

        return [self._mapear(linha) for linha in linhas]

    # ------------------------------------------------------------------
    # Mapeamento interno
    # ------------------------------------------------------------------

    @staticmethod
    def _mapear(linha: dict) -> Livros:
        return Livros(
            id=linha["id"],
            titulo=linha["titulo"],
            autor=linha["autor"],
            genero=linha["genero"],
            isbn=linha["isbn"],
            disponivel=bool(linha["disponivel"]),
        )