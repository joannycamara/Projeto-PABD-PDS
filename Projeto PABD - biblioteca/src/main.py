from negocio.produto_service import ProdutoService
from dados.conexao_singleton import ConexaoSingleton
from src.dados.livro_repository import ProdutoRepository
from apresentacao.interface_terminal import InterfaceTerminal


def principal() -> None:
    conexao = ConexaoSingleton.obter_conexao(
        tipo_banco="mysql",
        host="127.0.0.1",
        porta=3306,
        usuario="root",
        senha="labinfo",
        banco="aplicacao",
    )

    repositorio_produto = ProdutoRepository(conexao)
    servico_produto = ProdutoService(repositorio_produto)
    interface = InterfaceTerminal(servico_produto)

    try:
        interface.executar()
    finally:
        ConexaoSingleton.fechar_conexao()


if __name__ == "__main__":
    principal()
