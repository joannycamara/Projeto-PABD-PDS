from typing import Optional

from src.dados.livro_repository import ProdutoRepository
from src.dominio.livro import Produto


class ProdutoService:
    """Camada de negócio: aplica validações e regras simples."""

    def __init__(self, repositorio: ProdutoRepository) -> None:
        self.repositorio = repositorio

    def cadastrar_produto(self, nome: str, preco: float) -> Produto:
        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("O nome do produto nao pode ficar vazio.")

        if preco < 0:
            raise ValueError("O preco do produto nao pode ser negativo.")

        produto = Produto(id=None, nome=nome_limpo, preco=preco)
        novo_id = self.repositorio.adicionar(produto)
        produto.id = novo_id
        return produto

    def listar_produtos(self) -> list[Produto]:
        return self.repositorio.listar_todos()

    def buscar_produto_por_id(self, id_produto: int) -> Optional[Produto]:
        if id_produto <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")
        return self.repositorio.buscar_por_id(id_produto)

    def atualizar_produto(self, id_produto: int, nome: str, preco: float) -> bool:
        if id_produto <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")

        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("O nome do produto nao pode ficar vazio.")

        if preco < 0:
            raise ValueError("O preco do produto nao pode ser negativo.")

        produto = Produto(id=id_produto, nome=nome_limpo, preco=preco)
        return self.repositorio.atualizar(produto)

    def remover_produto(self, id_produto: int) -> bool:
        if id_produto <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")
        return self.repositorio.remover(id_produto)
