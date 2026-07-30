"""Menu principal da CLI, que direciona para os submenus de cada entidade."""
from src.interface.cli.cliente_cli import exibir_menu_cliente
from src.interface.cli.produto_cli import exibir_menu_produto
from src.servicos.servico_cliente import ServicoCliente
from src.servicos.servico_produto import ServicoProduto


def exibir_menu_principal(servico_cliente: ServicoCliente, servico_produto: ServicoProduto) -> None:
    while True:
        print("\n===== BackOffice B2B =====")
        print("1. Clientes")
        print("2. Produtos")
        print("0. Sair")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            exibir_menu_cliente(servico_cliente)
        elif opcao == "2":
            exibir_menu_produto(servico_produto)
        elif opcao == "0":
            print("\nAté logo!")
            return
        else:
            print("Opção inválida. Tente novamente.")