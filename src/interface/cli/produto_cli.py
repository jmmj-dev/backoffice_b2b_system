"""Interface de linha de comando para gestão de Produtos."""
from decimal import Decimal, InvalidOperation

from src.dominio.entidades.produto import Produto, UnidadeMedida
from src.servicos.servico_produto import ServicoProduto

MAPA_UNIDADES = {
    "1": UnidadeMedida.UNIDADE,
    "2": UnidadeMedida.CAIXA,
    "3": UnidadeMedida.QUILOGRAMA,
    "4": UnidadeMedida.LITRO,
    "5": UnidadeMedida.METRO,
    "6": UnidadeMedida.PACOTE,
}


def exibir_menu_produto(servico: ServicoProduto) -> None:
    while True:
        print("\n--- Produtos ---")
        print("1. Cadastrar novo produto")
        print("2. Listar produtos ativos")
        print("3. Buscar produto por id")
        print("4. Atualizar preço de um produto")
        print("5. Inativar produto")
        print("6. Reativar produto")
        print("0. Voltar")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            _cadastrar_produto(servico)
        elif opcao == "2":
            _listar_produtos_ativos(servico)
        elif opcao == "3":
            _buscar_produto_por_id(servico)
        elif opcao == "4":
            _atualizar_preco_produto(servico)
        elif opcao == "5":
            _inativar_produto(servico)
        elif opcao == "6":
            _reativar_produto(servico)
        elif opcao == "0":
            return
        else:
            print("Opção inválida. Tente novamente.")


def _cadastrar_produto(servico: ServicoProduto) -> None:
    print("\n-- Cadastrar novo produto --")
    nome = input("Nome: ").strip()

    print("Unidade de medida: 1=UN  2=CX  3=KG  4=L  5=M  6=PCT")
    unidade_input = input("Escolha: ").strip()
    unidade = MAPA_UNIDADES.get(unidade_input)
    if unidade is None:
        print("\n❌ Unidade de medida inválida.")
        return

    preco_input = input("Preço unitário (ex: 19.90): ").strip()
    descricao = input("Descrição (opcional): ").strip()

    try:
        preco = Decimal(preco_input)
        produto = Produto(nome=nome, unidade_medida=unidade, preco_unitario=preco, descricao=descricao)
        produto_salvo = servico.criar_produto(produto)
        print(f"\n✅ Produto cadastrado com sucesso! id = {produto_salvo.id}")
    except InvalidOperation:
        print("\n❌ Preço inválido. Use o formato 19.90 (ponto como separador decimal).")
    except ValueError as erro:
        print(f"\n❌ Erro ao cadastrar: {erro}")


def _listar_produtos_ativos(servico: ServicoProduto) -> None:
    print("\n-- Produtos ativos --")
    produtos = servico.listar_produtos_ativos()
    if not produtos:
        print("Nenhum produto ativo cadastrado.")
        return
    for produto in produtos:
        print(
            f"[{produto.id}] {produto.nome} ({produto.unidade_medida.value}) — {produto.preco_formatado()}"
        )


def _buscar_produto_por_id(servico: ServicoProduto) -> None:
    id_str = input("\nId do produto: ").strip()
    try:
        produto = servico.buscar_por_id(int(id_str))
        status = "ativo" if produto.ativo else "inativo"
        print(
            f"\n[{produto.id}] {produto.nome} ({status})\n"
            f"Unidade: {produto.unidade_medida.value}\n"
            f"Preço: {produto.preco_formatado()}\n"
            f"Descrição: {produto.descricao or '-'}"
        )
    except ValueError as erro:
        print(f"\n❌ {erro}")


def _atualizar_preco_produto(servico: ServicoProduto) -> None:
    id_str = input("\nId do produto: ").strip()
    try:
        produto = servico.buscar_por_id(int(id_str))
    except ValueError as erro:
        print(f"\n❌ {erro}")
        return

    print(f"Preço atual: {produto.preco_formatado()}")
    novo_preco_input = input("Novo preço (ex: 25.00): ").strip()

    try:
        produto.preco_unitario = Decimal(novo_preco_input)
        servico.atualizar_produto(produto)
        print("\n✅ Preço atualizado com sucesso!")
    except InvalidOperation:
        print("\n❌ Preço inválido. Use o formato 25.00 (ponto como separador decimal).")
    except ValueError as erro:
        print(f"\n❌ Erro ao atualizar: {erro}")


def _inativar_produto(servico: ServicoProduto) -> None:
    id_str = input("\nId do produto a inativar: ").strip()
    confirmacao = input(f"Confirma inativação do produto {id_str}? (s/n): ").strip().lower()
    if confirmacao != "s":
        print("Operação cancelada.")
        return
    try:
        servico.inativar_produto(int(id_str))
        print("\n✅ Produto inativado.")
    except ValueError as erro:
        print(f"\n❌ {erro}")


def _reativar_produto(servico: ServicoProduto) -> None:
    id_str = input("\nId do produto a reativar: ").strip()
    try:
        servico.reativar_produto(int(id_str))
        print("\n✅ Produto reativado.")
    except ValueError as erro:
        print(f"\n❌ {erro}")