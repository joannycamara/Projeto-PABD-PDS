from typing import Optional

import mysql.connector

from dominio.livro import Livros, Titulo


class LivrosRepository:
    """Camada de dados: acesso ao banco para as tabelas titulos + exemplares.

    Um TÍTULO é a ficha bibliográfica (titulo, autor, genero, isbn).
    Um EXEMPLAR é uma cópia física de um título (com sua própria
    disponibilidade). Os métodos de leitura retornam objetos `Livros`,
    que representam um exemplar já com os dados do título embutidos —
    isso mantém compatibilidade com o restante do sistema, que já espera
    ler .titulo, .autor, .isbn, .genero e .disponivel de cada "livro".
    """

    _SELECT_BASE = """
        SELECT e.id, e.disponivel, e.id_titulo,
               t.titulo, t.autor, t.genero, t.isbn
        FROM exemplares e
        JOIN titulos t ON t.id = e.id_titulo
    """

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao

    # ------------------------------------------------------------------
    # Escrita — Títulos
    # ------------------------------------------------------------------

    def adicionar_titulo_com_exemplares(self, titulo: str, autor: str, genero: str,
                                         isbn: str, quantidade: int) -> int:
        """Cria a ficha bibliográfica e `quantidade` exemplares disponíveis.
        Retorna o id do título criado."""
        cursor = self.conexao.cursor()
        cursor.execute(
            "INSERT INTO titulos (titulo, autor, genero, isbn) VALUES (%s, %s, %s, %s)",
            (titulo, autor, genero, isbn),
        )
        id_titulo = int(cursor.lastrowid)

        cursor.executemany(
            "INSERT INTO exemplares (id_titulo, disponivel) VALUES (%s, TRUE)",
            [(id_titulo,)] * quantidade,
        )

        self.conexao.commit()
        cursor.close()
        return id_titulo

    def adicionar_exemplar(self, id_titulo: int) -> int:
        """Adiciona mais um exemplar (cópia) a um título já existente."""
        cursor = self.conexao.cursor()
        cursor.execute(
            "INSERT INTO exemplares (id_titulo, disponivel) VALUES (%s, TRUE)",
            (id_titulo,),
        )
        self.conexao.commit()
        novo_id = int(cursor.lastrowid)
        cursor.close()
        return novo_id

    def atualizar_titulo(self, id_titulo: int, titulo: str, autor: str,
                          genero: str, isbn: str) -> bool:
        """Atualiza os dados bibliográficos (afeta todos os exemplares do título)."""
        cursor = self.conexao.cursor()
        cursor.execute(
            "UPDATE titulos SET titulo = %s, autor = %s, genero = %s, isbn = %s WHERE id = %s",
            (titulo, autor, genero, isbn, id_titulo),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados

    # ------------------------------------------------------------------
    # Escrita — Exemplares
    # ------------------------------------------------------------------

    def atualizar(self, livro: Livros) -> bool:
        """Compatibilidade: atualiza a disponibilidade do exemplar e os
        dados bibliográficos do título associado. Usado pelo EmprestimoService
        (só muda `disponivel`) e pelo LivroService (edição completa)."""
        cursor = self.conexao.cursor()
        cursor.execute(
            "UPDATE exemplares SET disponivel = %s WHERE id = %s",
            (livro.disponivel, livro.id),
        )
        id_titulo = livro.id_titulo
        if id_titulo is None:
            cursor.execute("SELECT id_titulo FROM exemplares WHERE id = %s", (livro.id,))
            linha = cursor.fetchone()
            id_titulo = linha[0] if linha else None

        afetados = cursor.rowcount > 0

        if id_titulo is not None:
            cursor.execute(
                "UPDATE titulos SET titulo = %s, autor = %s, genero = %s, isbn = %s WHERE id = %s",
                (livro.titulo, livro.autor, livro.genero, livro.isbn, id_titulo),
            )

        self.conexao.commit()
        cursor.close()
        return afetados

    def remover_exemplar(self, id_exemplar: int) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute("DELETE FROM exemplares WHERE id = %s", (id_exemplar,))
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados

    # ------------------------------------------------------------------
    # Leitura — Exemplares (view combinada com o título)
    # ------------------------------------------------------------------

    def listar_todos(self) -> list[Livros]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(self._SELECT_BASE + " ORDER BY t.titulo")
        linhas = cursor.fetchall()
        cursor.close()
        return [self._mapear(linha) for linha in linhas]

    def listar_por_disponibilidade(self, disponivel: bool) -> list[Livros]:
        """Retorna exemplares filtrados por disponibilidade. Usado em US09."""
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            self._SELECT_BASE + " WHERE e.disponivel = %s ORDER BY t.titulo",
            (disponivel,),
        )
        linhas = cursor.fetchall()
        cursor.close()
        return [self._mapear(linha) for linha in linhas]

    def buscar_por_id(self, id_exemplar: int) -> Optional[Livros]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(self._SELECT_BASE + " WHERE e.id = %s", (id_exemplar,))
        linha = cursor.fetchone()
        cursor.close()
        return self._mapear(linha) if linha else None

    def buscar_por_titulo_ou_autor(self, termo: str) -> list[Livros]:
        """Busca parcial por título ou autor. Usado em US04."""
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            self._SELECT_BASE + " WHERE t.titulo LIKE %s OR t.autor LIKE %s ORDER BY t.titulo",
            (f"%{termo}%", f"%{termo}%"),
        )
        linhas = cursor.fetchall()
        cursor.close()
        return [self._mapear(linha) for linha in linhas]

    # ------------------------------------------------------------------
    # Leitura — Títulos (ficha bibliográfica, sem duplicar por exemplar)
    # ------------------------------------------------------------------

    def listar_titulos(self) -> list[Titulo]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute("SELECT id, titulo, autor, genero, isbn FROM titulos ORDER BY titulo")
        linhas = cursor.fetchall()
        cursor.close()
        return [Titulo(**linha) for linha in linhas]

    def buscar_titulo_por_isbn(self, isbn: str) -> Optional[Titulo]:
        """Usado em US12 (evitar ISBN duplicado) e US13 (validar edição)."""
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute("SELECT id, titulo, autor, genero, isbn FROM titulos WHERE isbn = %s", (isbn,))
        linha = cursor.fetchone()
        cursor.close()
        return Titulo(**linha) if linha else None

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
            id_titulo=linha["id_titulo"],
        )