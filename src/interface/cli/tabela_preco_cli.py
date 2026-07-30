"""Interface de linha de comando para gestão de Tabelas de Preço."""
from decimal import Decimal, InvalidOperation

from src.dominio.entidades.tabela_preco import TabelaPreco, TipoItem
from src.servicos.servico_produto import ServicoProduto
from src.servicos.servico_servico import ServicoServico
from src.servicos.servico_tabela_preco import ServicoTabelaPreco


def exibir_menu_tabela_preco(
    servico_tabela: ServicoTabelaPreco, servico_produto: ServicoProduto, servico_servico: ServicoServico
) -> None:
    while True:
        print("\n--- Tabelas de Preço ---")
        print("1. Criar nova tabela de preço")
        print("2. Listar tabelas ativas")
        print("3. Ver detalhes de uma tabela (com itens)")
        print("4. Adicionar item (produto/serviço) a uma tabela")
        print("5. Atualizar preço de um item")
        print("6. Remover item de uma tabela")
        print("7. Inativar tabela")
        print("8. Reativar tabela")
        print("0. Voltar")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            _criar_tabela(servico_tabela)
        elif opcao == "2":
            _listar_tabelas_ativas(servico_tabela)
        elif opcao == "3":
            _ver_detalhes_tabela(servico_tabela, servico_produto, servico_servico)
        elif opcao == "4":
            _adicionar_item(servico_tabela, servico_produto, servico_servico)
        elif opcao == "5":
            _atualizar_preco_item(servico_tabela)
        elif opcao == "6":
            _remover_item(servico_tabela)
        elif opcao == "7":
            _inativar_tabela(servico_tabela)
        elif opcao == "8":
            _reativar_tabela(servico_tabela)
        elif opcao == "0":
            return
        else:
            print("Opção inválida. Tente novamente.")


def _criar_tabela(servico_tabela: ServicoTabelaPreco) -> None:
    print("\n-- Criar nova tabela de preço --")
    nome = input("Nome (ex: Varejo, Atacado): ").strip()
    descricao = input("Descrição (opcional): ").strip()
    try:
        tabela = servico_tabela.criar_tabela(TabelaPreco(nome=nome, descricao=descricao))
        print(f"\n✅ Tabela criada com sucesso! id = {tabela.id}")
    except ValueError as erro:
        print(f"\n❌ Erro ao criar: {erro}")


def _listar_tabelas_ativas(servico_tabela: ServicoTabelaPreco) -> None:
    print("\n-- Tabelas de preço ativas --")
    tabelas = servico_tabela.listar_tabelas_ativas()
    if not tabelas:
        print("Nenhuma tabela ativa cadastrada.")
        return
    for tabela in tabelas:
        print(f"[{tabela.id}] {tabela.nome} — {tabela.descricao or 'sem descrição'}")


def _ver_detalhes_tabela(
    servico_tabela: ServicoTabelaPreco, servico_produto: ServicoProduto, servico_servico: ServicoServico
) -> None:
    id_str = input("\nId da tabela: ").strip()
    try:
        tabela = servico_tabela.buscar_por_id(int(id_str))
    except ValueError as erro:
        print(f"\n❌ {erro}")
        return

    status = "ativa" if tabela.ativa else "inativa"
    print(f"\n[{tabela.id}] {tabela.nome} ({status}) — {tabela.descricao or 'sem descrição'}")

    itens_ativos = [item for item in tabela.itens if item.ativo]
    if not itens_ativos:
        print("Nenhum item cadastrado nesta tabela.")
        return

    print("Itens:")
    for item in itens_ativos:
        nome_item = _resolver_nome_item(item.tipo_item, item.referencia_id, servico_produto, servico_servico)
        print(f"  - {item.tipo_item.value} [{item.referencia_id}] {nome_item}: R$ {item.preco}")


def _adicionar_item(
    servico_tabela: ServicoTabelaPreco, servico_produto: ServicoProduto, servico_servico: ServicoServico
) -> None:
    tabela_id_str = input("\nId da tabela: ").strip()

    print("Tipo de item: 1 = Produto  2 = Serviço")
    tipo_input = input("Escolha: ").strip()
    if tipo_input == "1":
        tipo_item = TipoItem.PRODUTO
        print("\nProdutos ativos disponíveis:")
        for produto in servico_produto.listar_produtos_ativos():
            print(f"  [{produto.id}] {produto.nome} — {produto.preco_formatado()}")
    elif tipo_input == "2":
        tipo_item = TipoItem.SERVICO
        print("\nServiços ativos disponíveis:")
        for servico in servico_servico.listar_servicos_ativos():
            print(f"  [{servico.id}] {servico.nome} — {servico.valor_hora_formatado()}/h")
    else:
        print("\n❌ Tipo inválido.")
        return

    referencia_id_str = input("\nId do item escolhido: ").strip()
    preco_input = input("Preço nesta tabela (ex: 45.00): ").strip()

    try:
        item = servico_tabela.adicionar_item(
            int(tabela_id_str), tipo_item, int(referencia_id_str), Decimal(preco_input)
        )
        print(f"\n✅ Item adicionado com sucesso! preço = R$ {item.preco}")
    except InvalidOperation:
        print("\n❌ Preço inválido. Use o formato 45.00 (ponto como separador decimal).")
    except ValueError as erro:
        print(f"\n❌ Erro ao adicionar item: {erro}")


def _atualizar_preco_item(servico_tabela: ServicoTabelaPreco) -> None:
    tabela_id_str = input("\nId da tabela: ").strip()
    print("Tipo de item: 1 = Produto  2 = Serviço")
    tipo_input = input("Escolha: ").strip()
    tipo_item = TipoItem.PRODUTO if tipo_input == "1" else TipoItem.SERVICO

    referencia_id_str = input("Id do produto/serviço: ").strip()
    novo_preco_input = input("Novo preço (ex: 50.00): ").strip()

    try:
        servico_tabela.atualizar_preco_item(
            int(tabela_id_str), tipo_item, int(referencia_id_str), Decimal(novo_preco_input)
        )
        print("\n✅ Preço atualizado com sucesso!")
    except InvalidOperation:
        print("\n❌ Preço inválido. Use o formato 50.00 (ponto como separador decimal).")
    except ValueError as erro:
        print(f"\n❌ Erro ao atualizar: {erro}")


def _remover_item(servico_tabela: ServicoTabelaPreco) -> None:
    tabela_id_str = input("\nId da tabela: ").strip()
    print("Tipo de item: 1 = Produto  2 = Serviço")
    tipo_input = input("Escolha: ").strip()
    tipo_item = TipoItem.PRODUTO if tipo_input == "1" else TipoItem.SERVICO

    referencia_id_str = input("Id do produto/serviço a remover da tabela: ").strip()
    confirmacao = input("Confirma remoção deste item da tabela? (s/n): ").strip().lower()
    if confirmacao != "s":
        print("Operação cancelada.")
        return

    try:
        servico_tabela.remover_item(int(tabela_id_str), tipo_item, int(referencia_id_str))
        print("\n✅ Item removido da tabela.")
    except ValueError as erro:
        print(f"\n❌ {erro}")


def _inativar_tabela(servico_tabela: ServicoTabelaPreco) -> None:
    id_str = input("\nId da tabela a inativar: ").strip()
    confirmacao = input(f"Confirma inativação da tabela {id_str}? (s/n): ").strip().lower()
    if confirmacao != "s":
        print("Operação cancelada.")
        return
    try:
        servico_tabela.inativar_tabela(int(id_str))
        print("\n✅ Tabela inativada.")
    except ValueError as erro:
        print(f"\n❌ {erro}")


def _reativar_tabela(servico_tabela: ServicoTabelaPreco) -> None:
    id_str = input("\nId da tabela a reativar: ").strip()
    try:
        servico_tabela.reativar_tabela(int(id_str))
        print("\n✅ Tabela reativada.")
    except ValueError as erro:
        print(f"\n❌ {erro}")


def _resolver_nome_item(
    tipo_item: TipoItem, referencia_id: int, servico_produto: ServicoProduto, servico_servico: ServicoServico
) -> str:
    """Busca o nome do produto/serviço para exibição amigável na listagem de itens."""
    try:
        if tipo_item == TipoItem.PRODUTO:
            return servico_produto.buscar_por_id(referencia_id).nome
        return servico_servico.buscar_por_id(referencia_id).nome
    except ValueError:
        return "(não encontrado)"