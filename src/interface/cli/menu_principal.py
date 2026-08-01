"""Menu principal da CLI, que direciona para os submenus de cada entidade."""
from src.interface.cli.cliente_cli import exibir_menu_cliente
from src.interface.cli.orcamento_cli import exibir_menu_orcamento
from src.interface.cli.pedido_venda_cli import exibir_menu_pedido_venda
from src.interface.cli.produto_cli import exibir_menu_produto
from src.interface.cli.servico_cli import exibir_menu_servico
from src.interface.cli.tabela_preco_cli import exibir_menu_tabela_preco
from src.servicos.servico_cliente import ServicoCliente
from src.servicos.servico_orcamento import ServicoOrcamento
from src.servicos.servico_pedido_venda import ServicoPedidoVenda
from src.servicos.servico_produto import ServicoProduto
from src.servicos.servico_servico import ServicoServico
from src.servicos.servico_tabela_preco import ServicoTabelaPreco


def exibir_menu_principal(
    servico_cliente: ServicoCliente,
    servico_produto: ServicoProduto,
    servico_servico: ServicoServico,
    servico_tabela_preco: ServicoTabelaPreco,
    servico_orcamento: ServicoOrcamento,
    servico_pedido_venda: ServicoPedidoVenda,
) -> None:
    while True:
        print("\n===== BackOffice B2B =====")
        print("1. Clientes")
        print("2. Produtos")
        print("3. Serviços")
        print("4. Tabelas de Preço")
        print("5. Orçamentos")
        print("6. Pedidos de Venda")
        print("0. Sair")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            exibir_menu_cliente(servico_cliente, servico_tabela_preco)
        elif opcao == "2":
            exibir_menu_produto(servico_produto)
        elif opcao == "3":
            exibir_menu_servico(servico_servico)
        elif opcao == "4":
            exibir_menu_tabela_preco(servico_tabela_preco, servico_produto, servico_servico)
        elif opcao == "5":
            exibir_menu_orcamento(servico_orcamento, servico_cliente, servico_produto, servico_servico)
        elif opcao == "6":
            exibir_menu_pedido_venda(servico_pedido_venda, servico_orcamento)
        elif opcao == "0":
            print("\nAté logo!")
            return
        else:
            print("Opção inválida. Tente novamente.")