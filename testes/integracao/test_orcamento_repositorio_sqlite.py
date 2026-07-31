"""Testes de integração do OrcamentoRepositorioSQLite, incluindo persistência dos itens (agregado)."""
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from src.dominio.entidades.cliente import Cliente, TipoPessoa
from src.dominio.entidades.orcamento import Orcamento, StatusOrcamento
from src.dominio.entidades.tabela_preco import TabelaPreco, TipoItem
from src.infraestrutura.conexao import obter_caminho_banco, obter_conexao
from src.infraestrutura.schema import criar_tabelas
from src.repositorios.sqlite.cliente_repositorio_sqlite import ClienteRepositorioSQLite
from src.repositorios.sqlite.orcamento_repositorio_sqlite import OrcamentoRepositorioSQLite
from src.repositorios.sqlite.tabela_preco_repositorio_sqlite import TabelaPrecoRepositorioSQLite

CPF_VALIDO = "529.982.247-25"


@pytest.fixture
def contexto(monkeypatch):
    """Prepara um banco de TESTE isolado, já com um Cliente e uma TabelaPreco reais cadastrados,
    já que Orcamento tem chaves estrangeiras que o SQLite valida de verdade (PRAGMA foreign_keys = ON)."""
    monkeypatch.setenv("AMBIENTE", "teste")
    caminho = obter_caminho_banco()
    Path(caminho).unlink(missing_ok=True)

    conexao = obter_conexao()
    criar_tabelas(conexao)

    cliente = ClienteRepositorioSQLite(conexao).salvar(
        Cliente(
            nome="Cliente Teste",
            tipo_pessoa=TipoPessoa.FISICA,
            documento=CPF_VALIDO,
            email="teste@email.com",
            telefone="31900000000",
        )
    )
    tabela_preco = TabelaPrecoRepositorioSQLite(conexao).salvar(TabelaPreco(nome="Varejo"))

    repo_orcamento = OrcamentoRepositorioSQLite(conexao)

    yield repo_orcamento, cliente.id, tabela_preco.id

    conexao.close()
    Path(caminho).unlink(missing_ok=True)


def _criar_orcamento(cliente_id, tabela_preco_id, dias_validade=15):
    return Orcamento(
        cliente_id=cliente_id,
        tabela_preco_id=tabela_preco_id,
        data_validade=date.today() + timedelta(days=dias_validade),
    )


def test_salvar_orcamento_sem_itens(contexto):
    repositorio, cliente_id, tabela_preco_id = contexto
    orcamento = repositorio.salvar(_criar_orcamento(cliente_id, tabela_preco_id))
    assert orcamento.id is not None


def test_salvar_orcamento_com_itens_persiste_todos(contexto):
    repositorio, cliente_id, tabela_preco_id = contexto
    orcamento = _criar_orcamento(cliente_id, tabela_preco_id)
    orcamento.adicionar_item(
        TipoItem.PRODUTO, referencia_id=1, descricao="Parafuso", preco_unitario=Decimal("5.00"), quantidade=Decimal("10")
    )
    orcamento.adicionar_item(
        TipoItem.SERVICO, referencia_id=2, descricao="Instalação", preco_unitario=Decimal("100.00"), quantidade=Decimal("1")
    )
    repositorio.salvar(orcamento)

    recarregado = repositorio.buscar_por_id(orcamento.id)
    assert len(recarregado.itens) == 2
    assert recarregado.calcular_subtotal() == Decimal("150.00")


def test_buscar_por_id_preserva_status_e_desconto(contexto):
    repositorio, cliente_id, tabela_preco_id = contexto
    orcamento = _criar_orcamento(cliente_id, tabela_preco_id)
    orcamento.adicionar_item(
        TipoItem.PRODUTO, referencia_id=1, descricao="A", preco_unitario=Decimal("100.00"), quantidade=Decimal("1")
    )
    orcamento.aplicar_desconto(Decimal("10"))
    repositorio.salvar(orcamento)

    recarregado = repositorio.buscar_por_id(orcamento.id)
    assert recarregado.desconto_percentual == Decimal("10")
    assert recarregado.calcular_total() == Decimal("90.00")


def test_atualizar_status_e_persistido(contexto):
    repositorio, cliente_id, tabela_preco_id = contexto
    orcamento = _criar_orcamento(cliente_id, tabela_preco_id)
    orcamento.adicionar_item(
        TipoItem.PRODUTO, referencia_id=1, descricao="A", preco_unitario=Decimal("10.00"), quantidade=Decimal("1")
    )
    repositorio.salvar(orcamento)

    orcamento.enviar()
    repositorio.atualizar(orcamento)

    recarregado = repositorio.buscar_por_id(orcamento.id)
    assert recarregado.status == StatusOrcamento.ENVIADO


def test_remover_item_soft_delete_e_persistido(contexto):
    repositorio, cliente_id, tabela_preco_id = contexto
    orcamento = _criar_orcamento(cliente_id, tabela_preco_id)
    orcamento.adicionar_item(
        TipoItem.PRODUTO, referencia_id=1, descricao="A", preco_unitario=Decimal("10.00"), quantidade=Decimal("1")
    )
    repositorio.salvar(orcamento)

    item_id = orcamento.itens[0].id
    orcamento.remover_item(item_id)
    repositorio.atualizar(orcamento)

    recarregado = repositorio.buscar_por_id(orcamento.id)
    assert recarregado.calcular_subtotal() == Decimal("0")
    assert len(recarregado.itens) == 1  # item continua existindo, só inativo


def test_listar_por_cliente(contexto):
    repositorio, cliente_id, tabela_preco_id = contexto
    orcamento = _criar_orcamento(cliente_id, tabela_preco_id)
    repositorio.salvar(orcamento)

    orcamentos_do_cliente = repositorio.listar_por_cliente(cliente_id)
    assert len(orcamentos_do_cliente) == 1


def test_listar_todos_nao_carrega_itens(contexto):
    repositorio, cliente_id, tabela_preco_id = contexto
    orcamento = _criar_orcamento(cliente_id, tabela_preco_id)
    orcamento.adicionar_item(
        TipoItem.PRODUTO, referencia_id=1, descricao="A", preco_unitario=Decimal("10.00"), quantidade=Decimal("1")
    )
    repositorio.salvar(orcamento)

    listados = repositorio.listar_todos()
    assert len(listados) == 1
    assert listados[0].itens == []

def test_historico_e_persistido_e_recarregado(contexto):
    repositorio, cliente_id, tabela_preco_id = contexto
    orcamento = _criar_orcamento(cliente_id, tabela_preco_id)
    orcamento.adicionar_item(
        TipoItem.PRODUTO, referencia_id=1, descricao="A", preco_unitario=Decimal("10.00"), quantidade=Decimal("1")
    )
    orcamento.enviar()
    orcamento.adicionar_anotacao("Cliente pediu revisão de prazo.")
    repositorio.salvar(orcamento)

    recarregado = repositorio.buscar_por_id(orcamento.id)
    assert len(recarregado.historico) == 2
    assert recarregado.historico[0].tipo.value == "AUTOMATICO"
    assert recarregado.historico[1].tipo.value == "MANUAL"


def test_listar_todos_nao_carrega_historico(contexto):
    repositorio, cliente_id, tabela_preco_id = contexto
    orcamento = _criar_orcamento(cliente_id, tabela_preco_id)
    orcamento.adicionar_anotacao("Nota qualquer.")
    repositorio.salvar(orcamento)

    listados = repositorio.listar_todos()
    assert listados[0].historico == []    