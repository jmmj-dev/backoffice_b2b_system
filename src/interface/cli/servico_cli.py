"""Interface de linha de comando para gestão de Serviços prestados."""
from decimal import Decimal, InvalidOperation

from src.dominio.entidades.servico import Servico
from src.servicos.servico_servico import ServicoServico


def exibir_menu_servico(servico_app: ServicoServico) -> None:
    while True:
        print("\n--- Serviços ---")
        print("1. Cadastrar novo serviço")
        print("2. Listar serviços ativos")
        print("3. Buscar serviço por id")
        print("4. Atualizar valor/hora de um serviço")
        print("5. Inativar serviço")
        print("6. Reativar serviço")
        print("0. Voltar")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            _cadastrar_servico(servico_app)
        elif opcao == "2":
            _listar_servicos_ativos(servico_app)
        elif opcao == "3":
            _buscar_servico_por_id(servico_app)
        elif opcao == "4":
            _atualizar_valor_hora(servico_app)
        elif opcao == "5":
            _inativar_servico(servico_app)
        elif opcao == "6":
            _reativar_servico(servico_app)
        elif opcao == "0":
            return
        else:
            print("Opção inválida. Tente novamente.")


def _cadastrar_servico(servico_app: ServicoServico) -> None:
    print("\n-- Cadastrar novo serviço --")
    nome = input("Nome: ").strip()
    valor_hora_input = input("Valor por hora (ex: 150.00): ").strip()
    horas_input = input("Horas estimadas (ex: 10): ").strip()
    descricao = input("Descrição (opcional): ").strip()

    try:
        servico = Servico(
            nome=nome,
            valor_hora=Decimal(valor_hora_input),
            horas_estimadas=Decimal(horas_input),
            descricao=descricao,
        )
        salvo = servico_app.criar_servico(servico)
        print(f"\n✅ Serviço cadastrado com sucesso! id = {salvo.id}")
    except InvalidOperation:
        print("\n❌ Valor inválido. Use o formato 150.00 (ponto como separador decimal).")
    except ValueError as erro:
        print(f"\n❌ Erro ao cadastrar: {erro}")


def _listar_servicos_ativos(servico_app: ServicoServico) -> None:
    print("\n-- Serviços ativos --")
    servicos = servico_app.listar_servicos_ativos()
    if not servicos:
        print("Nenhum serviço ativo cadastrado.")
        return
    for servico in servicos:
        print(
            f"[{servico.id}] {servico.nome} — {servico.valor_hora_formatado()}/h "
            f"— estimativa: {servico.horas_estimadas}h"
        )


def _buscar_servico_por_id(servico_app: ServicoServico) -> None:
    id_str = input("\nId do serviço: ").strip()
    try:
        servico = servico_app.buscar_por_id(int(id_str))
        status = "ativo" if servico.ativo else "inativo"
        print(
            f"\n[{servico.id}] {servico.nome} ({status})\n"
            f"Valor/hora: {servico.valor_hora_formatado()}\n"
            f"Horas estimadas: {servico.horas_estimadas}\n"
            f"Valor total estimado: R$ {servico.calcular_valor_total_estimado()}\n"
            f"Descrição: {servico.descricao or '-'}"
        )
    except ValueError as erro:
        print(f"\n❌ {erro}")


def _atualizar_valor_hora(servico_app: ServicoServico) -> None:
    id_str = input("\nId do serviço: ").strip()
    try:
        servico = servico_app.buscar_por_id(int(id_str))
    except ValueError as erro:
        print(f"\n❌ {erro}")
        return

    print(f"Valor/hora atual: {servico.valor_hora_formatado()}")
    novo_valor_input = input("Novo valor/hora (ex: 180.00): ").strip()

    try:
        servico.valor_hora = Decimal(novo_valor_input)
        servico_app.atualizar_servico(servico)
        print("\n✅ Valor/hora atualizado com sucesso!")
    except InvalidOperation:
        print("\n❌ Valor inválido. Use o formato 180.00 (ponto como separador decimal).")
    except ValueError as erro:
        print(f"\n❌ Erro ao atualizar: {erro}")


def _inativar_servico(servico_app: ServicoServico) -> None:
    id_str = input("\nId do serviço a inativar: ").strip()
    confirmacao = input(f"Confirma inativação do serviço {id_str}? (s/n): ").strip().lower()
    if confirmacao != "s":
        print("Operação cancelada.")
        return
    try:
        servico_app.inativar_servico(int(id_str))
        print("\n✅ Serviço inativado.")
    except ValueError as erro:
        print(f"\n❌ {erro}")


def _reativar_servico(servico_app: ServicoServico) -> None:
    id_str = input("\nId do serviço a reativar: ").strip()
    try:
        servico_app.reativar_servico(int(id_str))
        print("\n✅ Serviço reativado.")
    except ValueError as erro:
        print(f"\n❌ {erro}")