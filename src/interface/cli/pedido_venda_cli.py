"""Interface de linha de comando para gestão de Pedidos de Venda."""
from src.servicos.servico_orcamento import ServicoOrcamento
from src.servicos.servico_pedido_venda import ServicoPedidoVenda


def exibir_menu_pedido_venda(
    servico_pedido: ServicoPedidoVenda, servico_orcamento: ServicoOrcamento
) -> None:
    while True:
        print("\n--- Pedidos de Venda ---")
        print("1. Gerar pedido a partir de orçamento aceito")
        print("2. Listar pedidos de um cliente")
        print("3. Listar todos os pedidos")
        print("4. Ver detalhes de um pedido")
        print("5. Avançar para 'Em separação'")
        print("6. Faturar")
        print("7. Marcar como entregue")
        print("8. Cancelar pedido")
        print("0. Voltar")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            _gerar_pedido(servico_pedido, servico_orcamento)
        elif opcao == "2":
            _listar_por_cliente(servico_pedido)
        elif opcao == "3":
            _listar_todos(servico_pedido)
        elif opcao == "4":
            _ver_detalhes(servico_pedido)
        elif opcao == "5":
            _avancar_para_em_separacao(servico_pedido)
        elif opcao == "6":
            _faturar(servico_pedido)
        elif opcao == "7":
            _marcar_como_entregue(servico_pedido)
        elif opcao == "8":
            _cancelar(servico_pedido)
        elif opcao == "0":
            return
        else:
            print("Opção inválida. Tente novamente.")


def _gerar_pedido(servico_pedido: ServicoPedidoVenda, servico_orcamento: ServicoOrcamento) -> None:
    print("\n-- Gerar pedido a partir de orçamento aceito --")
    print("Orçamentos cadastrados (verifique o status antes de escolher):")
    for orcamento in servico_orcamento.listar_todos():
        print(f"  [{orcamento.id}] cliente_id={orcamento.cliente_id} status={orcamento.status.value}")

    orcamento_id_str = input("\nId do orçamento: ").strip()
    try:
        pedido = servico_pedido.criar_a_partir_de_orcamento(int(orcamento_id_str))
        print(f"\n✅ Pedido de venda gerado com sucesso! id = {pedido.id} (status: {pedido.status.value})")
    except ValueError as erro:
        print(f"\n❌ Erro ao gerar pedido: {erro}")


def _listar_por_cliente(servico_pedido: ServicoPedidoVenda) -> None:
    cliente_id_str = input("\nId do cliente: ").strip()
    try:
        pedidos = servico_pedido.listar_por_cliente(int(cliente_id_str))
    except ValueError as erro:
        print(f"\n❌ {erro}")
        return

    if not pedidos:
        print("Nenhum pedido encontrado para este cliente.")
        return
    for pedido in pedidos:
        print(f"[{pedido.id}] status={pedido.status.value} total=R$ {pedido.calcular_total()}")


def _listar_todos(servico_pedido: ServicoPedidoVenda) -> None:
    print("\n-- Todos os pedidos de venda --")
    pedidos = servico_pedido.listar_todos()
    if not pedidos:
        print("Nenhum pedido cadastrado.")
        return
    for pedido in pedidos:
        print(
            f"[{pedido.id}] cliente_id={pedido.cliente_id} orcamento_id={pedido.orcamento_id} "
            f"status={pedido.status.value}"
        )


def _ver_detalhes(servico_pedido: ServicoPedidoVenda) -> None:
    id_str = input("\nId do pedido: ").strip()
    try:
        pedido = servico_pedido.buscar_por_id(int(id_str))
    except ValueError as erro:
        print(f"\n❌ {erro}")
        return

    print(f"\n[{pedido.id}] status={pedido.status.value}")
    print(f"Cliente: {pedido.cliente_id} | Orçamento de origem: {pedido.orcamento_id}")
    print(f"Criado em: {pedido.data_criacao.strftime('%d/%m/%Y %H:%M')}")

    print("Itens:")
    for item in pedido.itens:
        print(
            f"  [{item.id}] {item.descricao} — {item.quantidade} x R$ {item.preco_unitario} "
            f"= R$ {item.calcular_subtotal()}"
        )

    print(f"\nTotal: R$ {pedido.calcular_total()}")


def _avancar_para_em_separacao(servico_pedido: ServicoPedidoVenda) -> None:
    id_str = input("\nId do pedido: ").strip()
    try:
        servico_pedido.avancar_para_em_separacao(int(id_str))
        print("\n✅ Pedido em separação.")
    except ValueError as erro:
        print(f"\n❌ {erro}")


def _faturar(servico_pedido: ServicoPedidoVenda) -> None:
    id_str = input("\nId do pedido: ").strip()
    try:
        servico_pedido.faturar(int(id_str))
        print("\n✅ Pedido faturado.")
    except ValueError as erro:
        print(f"\n❌ {erro}")


def _marcar_como_entregue(servico_pedido: ServicoPedidoVenda) -> None:
    id_str = input("\nId do pedido: ").strip()
    confirmacao = input(f"Confirma entrega do pedido {id_str}? (s/n): ").strip().lower()
    if confirmacao != "s":
        print("Operação cancelada.")
        return
    try:
        servico_pedido.marcar_como_entregue(int(id_str))
        print("\n✅ Pedido marcado como entregue.")
    except ValueError as erro:
        print(f"\n❌ {erro}")


def _cancelar(servico_pedido: ServicoPedidoVenda) -> None:
    id_str = input("\nId do pedido a cancelar: ").strip()
    confirmacao = input(f"Confirma cancelamento do pedido {id_str}? (s/n): ").strip().lower()
    if confirmacao != "s":
        print("Operação cancelada.")
        return
    try:
        servico_pedido.cancelar(int(id_str))
        print("\n✅ Pedido cancelado.")
    except ValueError as erro:
        print(f"\n❌ {erro}")