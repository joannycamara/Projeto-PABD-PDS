from typing import Optional

from dados.livro_repository import LivrosRepository
from dominio.livro import Livros, Titulo


class LivroService:
    """Camada de negócio: regras relacionadas ao acervo (US04, US09, US12, US13, US14).

    Trabalha com dois conceitos:
    - TÍTULO: a ficha bibliográfica (titulo, autor, genero, isbn) — cadastrada uma vez.
    - EXEMPLAR: uma cópia física de um título — pode haver várias por título,
      cada uma com sua própria disponibilidade.
    """

    def __init__(self, repositorio: LivrosRepository) -> None:
        self.repositorio = repositorio

    # ------------------------------------------------------------------
    # US12 — Cadastrar Livro / novo título (bibliotecário)
    # ------------------------------------------------------------------

    def cadastrar_livro(self, titulo: str, autor: str, genero: str, isbn: str,
                         quantidade: int = 1) -> int:
        """Cadastra um novo título e cria `quantidade` exemplares para ele.
        Retorna o id do título criado."""
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

        if quantidade < 1:
            raise ValueError("A quantidade de exemplares deve ser pelo menos 1.")

        if self.repositorio.buscar_titulo_por_isbn(isbn_limpo) is not None:
            raise ValueError(
                "Já existe um título cadastrado com este ISBN. "
                "Use \"+ Exemplar\" para adicionar outra cópia a ele."
            )

        return self.repositorio.adicionar_titulo_com_exemplares(
            titulo_limpo, autor_limpo, genero_limpo, isbn_limpo, quantidade
        )

    def adicionar_exemplar(self, id_exemplar_referencia: int) -> int:
        """Adiciona mais um exemplar ao mesmo título de um exemplar já existente
        (usado pelo botão "+ Exemplar" na tela do bibliotecário)."""
        livro = self.repositorio.buscar_por_id(id_exemplar_referencia)
        if livro is None:
            raise ValueError("Livro não encontrado.")
        return self.repositorio.adicionar_exemplar(livro.id_titulo)

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
        """id_livro é o id do EXEMPLAR selecionado na tela; a edição altera
        o TÍTULO ao qual esse exemplar pertence (afetando todas as cópias)."""
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

        id_titulo = livro_existente.id_titulo

        # Garante que o ISBN novo não pertence a outro título
        titulo_com_isbn = self.repositorio.buscar_titulo_por_isbn(isbn_limpo)
        if titulo_com_isbn is not None and titulo_com_isbn.id != id_titulo:
            raise ValueError("ISBN já cadastrado para outro título.")

        return self.repositorio.atualizar_titulo(
            id_titulo, titulo_limpo, autor_limpo, genero.strip(), isbn_limpo
        )

    # ------------------------------------------------------------------
    # US14 — Remover Livro do Acervo (bibliotecário)
    # ------------------------------------------------------------------

    def remover_livro(self, id_livro: int, tem_emprestimo_ativo: bool, tem_reserva_ativa: bool) -> bool:
        """Remove UM exemplar (a cópia selecionada) após verificações de negócio.

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

        return self.repositorio.remover_exemplar(id_livro)

    # ------------------------------------------------------------------
    # Operações de suporte usadas por outros services
    # ------------------------------------------------------------------

    def buscar_por_id(self, id_livro: int) -> Optional[Livros]:
        if id_livro <= 0:
            raise ValueError("O ID deve ser um número inteiro positivo.")
        return self.repositorio.buscar_por_id(id_livro)

    def listar_livros(self) -> list[Livros]:
        """Lista os EXEMPLARES (uma linha por cópia física)."""
        return self.repositorio.listar_todos()

    def listar_titulos(self) -> list[Titulo]:
        """Lista os TÍTULOS distintos do acervo (fichas bibliográficas),
        sem duplicar por exemplar. Usado no card 'Títulos no Acervo'."""
        return self.repositorio.listar_titulos()

    def marcar_disponivel(self, id_livro: int, disponivel: bool) -> None:
        """Atualiza a flag disponivel do exemplar. Chamado pelo EmprestimoService."""
        livro = self.repositorio.buscar_por_id(id_livro)
        if livro is None:
            raise ValueError("Livro não encontrado.")
        livro.disponivel = disponivel
        self.repositorio.atualizar(livro)