"""Interface de linha de comando para gestão de Orçamentos."""
from decimal import Decimal, InvalidOperation

from src.dominio.entidades.tabela_preco import TipoItem
from src.interface.cli.formatadores_cli import formatar_data_br, ler_data_br
from src.servicos.servico_cliente import ServicoCliente
from src.servicos.servico_orcamento import ServicoOrcamento
from src.servicos.servico_produto import ServicoProduto
from src.servicos.servico_servico import ServicoServico


def exibir_menu_orcamento(
    servico_orcamento: ServicoOrcamento,
    servico_cliente: ServicoCliente,
    servico_produto: ServicoProduto,
    servico_servico: ServicoServico,
) -> None:
    while True:
        print("\n--- Orçamentos ---")
        print("1. Criar novo orçamento")
        print("2. Listar orçamentos de um cliente")
        print("3. Listar todos os orçamentos")
        print("4. Ver detalhes de um orçamento")
        print("5. Adicionar item a um orçamento")
        print("6. Remover item de um orçamento")
        print("7. Aplicar desconto")
        print("8. Enviar orçamento")
        print("9. Aceitar orçamento")
        print("10. Recusar orçamento")
        print("11. Adicionar anotação ao histórico")
        print("0. Voltar")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            _criar_orcamento(servico_orcamento, servico_cliente)
        elif opcao == "2":
            _listar_por_cliente(servico_orcamento)
        elif opcao == "3":
            _listar_todos(servico_orcamento)
        elif opcao == "4":
            _ver_detalhes(servico_orcamento)
        elif opcao == "5":
            _adicionar_item(servico_orcamento, servico_produto, servico_servico)
        elif opcao == "6":
            _remover_item(servico_orcamento)
        elif opcao == "7":
            _aplicar_desconto(servico_orcamento)
        elif opcao == "8":
            _enviar(servico_orcamento)
        elif opcao == "9":
            _aceitar(servico_orcamento)
        elif opcao == "10":
            _recusar(servico_orcamento)
        elif opcao == "11":
            _adicionar_anotacao(servico_orcamento)
        elif opcao == "0":
            return
        else:
            print("Opção inválida. Tente novamente.")


def _criar_orcamento(servico_orcamento: ServicoOrcamento, servico_cliente: ServicoCliente) -> None:
    print("\n-- Criar novo orçamento --")
    print("Clientes ativos disponíveis:")
    for cliente in servico_cliente.listar_clientes_ativos():
        tabela_info = f"tabela_preco_id={cliente.tabela_preco_id}" if cliente.tabela_preco_id else "sem tabela"
        print(f"  [{cliente.id}] {cliente.nome} ({tabela_info})")

    cliente_id_str = input("\nId do cliente: ").strip()
    data_validade_str = input("Data de validade (DD/MM/AAAA): ").strip()

    try:
        data_validade = ler_data_br(data_validade_str)
        orcamento = servico_orcamento.criar_orcamento(int(cliente_id_str), data_validade)
        print(f"\n✅ Orçamento criado com sucesso! id = {orcamento.id} (status: {orcamento.status.value})")
    except ValueError as erro:
        print(f"\n❌ Erro ao criar: {erro}")


def _listar_por_cliente(servico_orcamento: ServicoOrcamento) -> None:
    cliente_id_str = input("\nId do cliente: ").strip()
    try:
        orcamentos = servico_orcamento.listar_por_cliente(int(cliente_id_str))
    except ValueError as erro:
        print(f"\n❌ {erro}")
        return

    if not orcamentos:
        print("Nenhum orçamento encontrado para este cliente.")
        return
    for orcamento in orcamentos:
        print(
            f"[{orcamento.id}] status={orcamento.status.value} "
            f"validade={formatar_data_br(orcamento.data_validade)} "
            f"total=R$ {orcamento.calcular_total()}"
        )


def _listar_todos(servico_orcamento: ServicoOrcamento) -> None:
    print("\n-- Todos os orçamentos --")
    orcamentos = servico_orcamento.listar_todos()
    if not orcamentos:
        print("Nenhum orçamento cadastrado.")
        return
    for orcamento in orcamentos:
        print(
            f"[{orcamento.id}] cliente_id={orcamento.cliente_id} status={orcamento.status.value} "
            f"validade={formatar_data_br(orcamento.data_validade)}"
        )


def _ver_detalhes(servico_orcamento: ServicoOrcamento) -> None:
    id_str = input("\nId do orçamento: ").strip()
    try:
        orcamento = servico_orcamento.buscar_por_id(int(id_str))
    except ValueError as erro:
        print(f"\n❌ {erro}")
        return

    print(f"\n[{orcamento.id}] status={orcamento.status.value}")
    print(f"Cliente: {orcamento.cliente_id} | Tabela de preço: {orcamento.tabela_preco_id}")
    print(f"Validade: {formatar_data_br(orcamento.data_validade)}")

    itens_ativos = [item for item in orcamento.itens if item.ativo]
    if not itens_ativos:
        print("Nenhum item cadastrado.")
    else:
        print("Itens:")
        for item in itens_ativos:
            print(
                f"  [{item.id}] {item.descricao} — {item.quantidade} x R$ {item.preco_unitario} "
                f"= R$ {item.calcular_subtotal()}"
            )

    print(f"\nSubtotal: R$ {orcamento.calcular_subtotal()}")
    print(f"Desconto ({orcamento.desconto_percentual}%): R$ {orcamento.calcular_valor_desconto()}")
    print(f"Total: R$ {orcamento.calcular_total()}")

    if orcamento.historico:
        print("\nHistórico de negociação:")
        for registro in orcamento.historico:
            marca = "🤖" if registro.tipo.value == "AUTOMATICO" else "📝"
            print(f"  {marca} [{registro.data_hora.strftime('%d/%m/%Y %H:%M')}] {registro.descricao}")


def _adicionar_item(
    servico_orcamento: ServicoOrcamento, servico_produto: ServicoProduto, servico_servico: ServicoServico
) -> None:
    orcamento_id_str = input("\nId do orçamento: ").strip()

    print("Tipo de item: 1 = Produto  2 = Serviço")
    tipo_input = input("Escolha: ").strip()
    if tipo_input == "1":
        tipo_item = TipoItem.PRODUTO
        print("\nProdutos ativos disponíveis:")
        for produto in servico_produto.listar_produtos_ativos():
            print(f"  [{produto.id}] {produto.nome}")
    elif tipo_input == "2":
        tipo_item = TipoItem.SERVICO
        print("\nServiços ativos disponíveis:")
        for servico in servico_servico.listar_servicos_ativos():
            print(f"  [{servico.id}] {servico.nome}")
    else:
        print("\n❌ Tipo inválido.")
        return

    referencia_id_str = input("\nId do item escolhido: ").strip()
    quantidade_str = input("Quantidade: ").strip()

    try:
        item = servico_orcamento.adicionar_item(
            int(orcamento_id_str), tipo_item, int(referencia_id_str), Decimal(quantidade_str)
        )
        print(f"\n✅ Item adicionado! {item.descricao} — preço unitário: R$ {item.preco_unitario}")
    except InvalidOperation:
        print("\n❌ Quantidade inválida.")
    except ValueError as erro:
        print(f"\n❌ Erro ao adicionar item: {erro}")


def _remover_item(servico_orcamento: ServicoOrcamento) -> None:
    orcamento_id_str = input("\nId do orçamento: ").strip()
    item_id_str = input("Id do item a remover: ").strip()
    confirmacao = input("Confirma remoção deste item? (s/n): ").strip().lower()
    if confirmacao != "s":
        print("Operação cancelada.")
        return
    try:
        servico_orcamento.remover_item(int(orcamento_id_str), int(item_id_str))
        print("\n✅ Item removido.")
    except ValueError as erro:
        print(f"\n❌ {erro}")


def _aplicar_desconto(servico_orcamento: ServicoOrcamento) -> None:
    orcamento_id_str = input("\nId do orçamento: ").strip()
    percentual_str = input("Percentual de desconto (ex: 10): ").strip()
    try:
        servico_orcamento.aplicar_desconto(int(orcamento_id_str), Decimal(percentual_str))
        print("\n✅ Desconto aplicado.")
    except InvalidOperation:
        print("\n❌ Percentual inválido.")
    except ValueError as erro:
        print(f"\n❌ Erro ao aplicar desconto: {erro}")


def _enviar(servico_orcamento: ServicoOrcamento) -> None:
    id_str = input("\nId do orçamento a enviar: ").strip()
    try:
        servico_orcamento.enviar_orcamento(int(id_str))
        print("\n✅ Orçamento enviado.")
    except ValueError as erro:
        print(f"\n❌ {erro}")


def _aceitar(servico_orcamento: ServicoOrcamento) -> None:
    id_str = input("\nId do orçamento a aceitar: ").strip()
    try:
        servico_orcamento.aceitar_orcamento(int(id_str))
        print("\n✅ Orçamento aceito.")
    except ValueError as erro:
        print(f"\n❌ {erro}")


def _recusar(servico_orcamento: ServicoOrcamento) -> None:
    id_str = input("\nId do orçamento a recusar: ").strip()
    confirmacao = input(f"Confirma recusa do orçamento {id_str}? (s/n): ").strip().lower()
    if confirmacao != "s":
        print("Operação cancelada.")
        return
    try:
        servico_orcamento.recusar_orcamento(int(id_str))
        print("\n✅ Orçamento recusado.")
    except ValueError as erro:
        print(f"\n❌ {erro}")

def _adicionar_anotacao(servico_orcamento: ServicoOrcamento) -> None:
    id_str = input("\nId do orçamento: ").strip()
    texto = input("Anotação: ").strip()
    try:
        servico_orcamento.adicionar_anotacao(int(id_str), texto)
        print("\n✅ Anotação adicionada ao histórico.")
    except ValueError as erro:
        print(f"\n❌ {erro}")        