from negocio.produto_service import ProdutoService


class InterfaceTerminal:
    """Camada apresentação: conversa com o usuario pelo terminal."""

    def __init__(self, servico: ProdutoService) -> None:
        self.servico = servico

    def executar(self) -> None:
        while True:
            self._mostrar_menu()
            opcao = input("Escolha uma opcao: ").strip()
            print()

            try:
                if opcao == "1":
                    self._cadastrar_produto()
                elif opcao == "2":
                    self._listar_produtos()
                elif opcao == "3":
                    self._buscar_produto_por_id()
                elif opcao == "4":
                    self._atualizar_produto()
                elif opcao == "5":
                    self._remover_produto()
                elif opcao == "0":
                    print("Encerrando o programa...")
                    break
                else:
                    print("Opcao invalida. Tente novamente.")
            except ValueError as erro:
                print(f"Erro: {erro}")
            except Exception as erro:
                print(f"Erro inesperado: {erro}")

            print("\n" + "-" * 50 + "\n")

    def _mostrar_menu(self) -> None:
        print("=" * 50)
        print("CADASTRO DE PRODUTOS")
        print("=" * 50)
        print("1 - Cadastrar produto")
        print("2 - Listar produtos")
        print("3 - Buscar produto por ID")
        print("4 - Atualizar produto")
        print("5 - Remover produto")
        print("0 - Sair")
        print("=" * 50)

    def _cadastrar_produto(self) -> None:
        nome = input("Nome do produto: ")
        preco = self._ler_preco("Preco do produto: ")
        produto = self.servico.cadastrar_produto(nome, preco)
        print(f"Produto cadastrado com sucesso. ID gerado: {produto.id}")

    def _listar_produtos(self) -> None:
        produtos = self.servico.listar_produtos()
        if not produtos:
            print("Nenhum produto cadastrado.")
            return

        print("Produtos cadastrados:")
        for produto in produtos:
            print(f"ID: {produto.id} | Nome: {produto.nome} | Preco: R$ {produto.preco:.2f}")

    def _buscar_produto_por_id(self) -> None:
        id_produto = self._ler_inteiro("Informe o ID do produto: ")
        produto = self.servico.buscar_produto_por_id(id_produto)

        if produto is None:
            print("Produto nao encontrado.")
            return

        print(f"ID: {produto.id}")
        print(f"Nome: {produto.nome}")
        print(f"Preco: R$ {produto.preco:.2f}")

    def _atualizar_produto(self) -> None:
        id_produto = self._ler_inteiro("Informe o ID do produto a ser atualizado: ")
        nome = input("Novo nome do produto: ")
        preco = self._ler_preco("Novo preco do produto: ")

        foi_atualizado = self.servico.atualizar_produto(id_produto, nome, preco)
        if foi_atualizado:
            print("Produto atualizado com sucesso.")
        else:
            print("Nenhum produto foi atualizado. Verifique o ID informado.")

    def _remover_produto(self) -> None:
        id_produto = self._ler_inteiro("Informe o ID do produto a ser removido: ")
        foi_removido = self.servico.remover_produto(id_produto)
        if foi_removido:
            print("Produto removido com sucesso.")
        else:
            print("Nenhum produto foi removido. Verifique o ID informado.")

    @staticmethod
    def _ler_inteiro(mensagem: str) -> int:
        valor_bruto = input(mensagem).strip()
        return int(valor_bruto)

    @staticmethod
    def _ler_preco(mensagem: str) -> float:
        valor_bruto = input(mensagem).strip().replace(",", ".")
        return float(valor_bruto)
