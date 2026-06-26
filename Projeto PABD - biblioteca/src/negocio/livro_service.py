from typing import Optional

from dados.livro_repository import LivrosRepository
from dominio.livro import Livros


class LivroService:
    """Camada de negócio: regras relacionadas ao acervo (US04, US09, US12, US13, US14)."""

    def __init__(self, repositorio: LivrosRepository) -> None:
        self.repositorio = repositorio

    # ------------------------------------------------------------------
    # US12 — Cadastrar Livro (bibliotecário)
    # ------------------------------------------------------------------

    def cadastrar_livro(self, titulo: str, autor: str, genero: str, isbn: str) -> Livros:
        titulo_limpo = titulo.strip()
        autor_limpo = autor.strip()
        genero_limpo = genero.strip()
        isbn_limpo = isbn.strip()

        if not titulo_limpo:
            raise ValueError("Preencha todos os campos obrigatórios.")

        if not autor_limpo:
            raise ValueError("Preencha todos os campos obrigatórios.")

        if not isbn_limpo:
            raise ValueError("Preencha todos os campos obrigatórios.")

        if self.repositorio.buscar_por_isbn(isbn_limpo) is not None:
            raise ValueError("Livro já cadastrado.")

        livro = Livros(id=None, titulo=titulo_limpo, autor=autor_limpo, genero=genero_limpo, isbn=isbn_limpo, disponivel=True)
        novo_id = self.repositorio.adicionar(livro)
        livro.id = novo_id
        return livro

    # ------------------------------------------------------------------
    # US04 — Buscar Livros (aluno)
    # ------------------------------------------------------------------

    def buscar_por_titulo_ou_autor(self, termo: str) -> list[Livros]:
        termo_limpo = termo.strip()
        if not termo_limpo:
            raise ValueError("Informe um termo para a busca.")
        resultados = self.repositorio.buscar_por_titulo_ou_autor(termo_limpo)
        return resultados  # lista vazia indica "nenhum resultado encontrado"

    # ------------------------------------------------------------------
    # US09 — Visualizar Livros Indisponíveis (bolsista)
    # ------------------------------------------------------------------

    def listar_indisponiveis(self) -> list[Livros]:
        return self.repositorio.listar_por_disponibilidade(disponivel=False)

    # ------------------------------------------------------------------
    # US13 — Editar Cadastro de Livro (bibliotecário)
    # ------------------------------------------------------------------

    def atualizar_livro(self, id_livro: int, titulo: str, autor: str, genero: str, isbn: str) -> bool:
        if id_livro <= 0:
            raise ValueError("O ID deve ser um número inteiro positivo.")

        titulo_limpo = titulo.strip()
        autor_limpo = autor.strip()
        isbn_limpo = isbn.strip()

        if not titulo_limpo or not autor_limpo or not isbn_limpo:
            raise ValueError("Preencha todos os campos obrigatórios.")

        livro_existente = self.repositorio.buscar_por_id(id_livro)
        if livro_existente is None:
            raise ValueError("Nenhum livro encontrado para os dados informados.")

        # Garante que o ISBN novo não pertence a outro livro
        livro_com_isbn = self.repositorio.buscar_por_isbn(isbn_limpo)
        if livro_com_isbn is not None and livro_com_isbn.id != id_livro:
            raise ValueError("ISBN já cadastrado para outro livro.")

        livro = Livros(
            id=id_livro,
            titulo=titulo_limpo,
            autor=autor_limpo,
            genero=genero.strip(),
            isbn=isbn_limpo,
            disponivel=livro_existente.disponivel,
        )
        return self.repositorio.atualizar(livro)

    # ------------------------------------------------------------------
    # US14 — Remover Livro do Acervo (bibliotecário)
    # ------------------------------------------------------------------

    def remover_livro(self, id_livro: int, tem_emprestimo_ativo: bool, tem_reserva_ativa: bool) -> bool:
        """Remove o livro após verificações de negócio.

        As flags tem_emprestimo_ativo e tem_reserva_ativa devem ser
        consultadas pelo chamador nos respectivos services antes de
        invocar este método.
        """
        if id_livro <= 0:
            raise ValueError("O ID deve ser um número inteiro positivo.")

        if self.repositorio.buscar_por_id(id_livro) is None:
            raise ValueError("Nenhum livro encontrado para os dados informados.")

        if tem_emprestimo_ativo:
            raise ValueError("Não é possível remover. O livro possui empréstimo ativo.")

        if tem_reserva_ativa:
            raise ValueError("Não é possível remover. O livro possui reserva ativa.")

        return self.repositorio.remover(id_livro)

    # ------------------------------------------------------------------
    # Operações de suporte usadas por outros services
    # ------------------------------------------------------------------

    def buscar_por_id(self, id_livro: int) -> Optional[Livros]:
        if id_livro <= 0:
            raise ValueError("O ID deve ser um número inteiro positivo.")
        return self.repositorio.buscar_por_id(id_livro)

    def listar_livros(self) -> list[Livros]:
        return self.repositorio.listar_todos()

    def marcar_disponivel(self, id_livro: int, disponivel: bool) -> None:
        """Atualiza a flag disponivel do livro. Chamado pelo EmprestimoService."""
        livro = self.repositorio.buscar_por_id(id_livro)
        if livro is None:
            raise ValueError("Livro não encontrado.")
        livro.disponivel = disponivel
        self.repositorio.atualizar(livro)