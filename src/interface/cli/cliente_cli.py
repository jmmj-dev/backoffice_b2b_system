"""Interface de linha de comando para gestão de Clientes."""
from decimal import Decimal

from src.dominio.entidades.cliente import Cliente, TipoPessoa
from src.servicos.servico_cliente import ServicoCliente


def exibir_menu_cliente(servico: ServicoCliente) -> None:
    """Loop do submenu de Cliente. Retorna quando o usuário escolhe voltar."""
    while True:
        print("\n--- Clientes ---")
        print("1. Cadastrar novo cliente")
        print("2. Listar clientes ativos")
        print("3. Buscar cliente por id")
        print("4. Atualizar telefone/email de um cliente")
        print("5. Inativar cliente")
        print("6. Reativar cliente")
        print("0. Voltar")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            _cadastrar_cliente(servico)
        elif opcao == "2":
            _listar_clientes_ativos(servico)
        elif opcao == "3":
            _buscar_cliente_por_id(servico)
        elif opcao == "4":
            _atualizar_contato_cliente(servico)
        elif opcao == "5":
            _inativar_cliente(servico)
        elif opcao == "6":
            _reativar_cliente(servico)
        elif opcao == "0":
            return
        else:
            print("Opção inválida. Tente novamente.")


def _cadastrar_cliente(servico: ServicoCliente) -> None:
    print("\n-- Cadastrar novo cliente --")
    nome = input("Nome: ").strip()

    tipo_input = input("Tipo (1 = Pessoa Física, 2 = Pessoa Jurídica): ").strip()
    tipo_pessoa = TipoPessoa.FISICA if tipo_input == "1" else TipoPessoa.JURIDICA

    documento = input("CPF/CNPJ: ").strip()
    email = input("E-mail: ").strip()
    telefone = input("Telefone: ").strip()

    try:
        cliente = Cliente(
            nome=nome, tipo_pessoa=tipo_pessoa, documento=documento, email=email, telefone=telefone
        )
        cliente_salvo = servico.criar_cliente(cliente)
        print(f"\n✅ Cliente cadastrado com sucesso! id = {cliente_salvo.id}")
    except ValueError as erro:
        print(f"\n❌ Erro ao cadastrar: {erro}")


def _listar_clientes_ativos(servico: ServicoCliente) -> None:
    print("\n-- Clientes ativos --")
    clientes = servico.listar_clientes_ativos()
    if not clientes:
        print("Nenhum cliente ativo cadastrado.")
        return
    for cliente in clientes:
        print(f"[{cliente.id}] {cliente.nome} — {cliente.documento_formatado()} — {cliente.email}")


def _buscar_cliente_por_id(servico: ServicoCliente) -> None:
    id_str = input("\nId do cliente: ").strip()
    try:
        cliente = servico.buscar_por_id(int(id_str))
        status = "ativo" if cliente.ativo else "inativo"
        print(
            f"\n[{cliente.id}] {cliente.nome} ({status})\n"
            f"Documento: {cliente.documento_formatado()}\n"
            f"E-mail: {cliente.email}\n"
            f"Telefone: {cliente.telefone}"
        )
    except ValueError as erro:
        print(f"\n❌ {erro}")


def _atualizar_contato_cliente(servico: ServicoCliente) -> None:
    id_str = input("\nId do cliente a atualizar: ").strip()
    try:
        cliente = servico.buscar_por_id(int(id_str))
    except ValueError as erro:
        print(f"\n❌ {erro}")
        return

    print(f"Telefone atual: {cliente.telefone} — deixe em branco para não alterar")
    novo_telefone = input("Novo telefone: ").strip()
    if novo_telefone:
        cliente.telefone = novo_telefone

    print(f"E-mail atual: {cliente.email} — deixe em branco para não alterar")
    novo_email = input("Novo e-mail: ").strip()
    if novo_email:
        cliente.email = novo_email

    try:
        servico.atualizar_cliente(cliente)
        print("\n✅ Cliente atualizado com sucesso!")
    except ValueError as erro:
        print(f"\n❌ Erro ao atualizar: {erro}")


def _inativar_cliente(servico: ServicoCliente) -> None:
    id_str = input("\nId do cliente a inativar: ").strip()
    confirmacao = input(f"Confirma inativação do cliente {id_str}? (s/n): ").strip().lower()
    if confirmacao != "s":
        print("Operação cancelada.")
        return
    try:
        servico.inativar_cliente(int(id_str))
        print("\n✅ Cliente inativado.")
    except ValueError as erro:
        print(f"\n❌ {erro}")


def _reativar_cliente(servico: ServicoCliente) -> None:
    id_str = input("\nId do cliente a reativar: ").strip()
    try:
        servico.reativar_cliente(int(id_str))
        print("\n✅ Cliente reativado.")
    except ValueError as erro:
        print(f"\n❌ {erro}")