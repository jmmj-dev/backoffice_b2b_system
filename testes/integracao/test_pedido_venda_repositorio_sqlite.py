"""Testes de integração do PedidoVendaRepositorioSQLite."""
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from src.dominio.entidades.cliente import Cliente, TipoPessoa
from src.dominio.entidades.orcamento import Orcamento
from src.dominio.entidades.pedido_venda import ItemPedidoVenda, PedidoVenda, StatusPedidoVenda
from src.dominio.entidades.tabela_preco import TabelaPreco, TipoItem
from src.infraestrutura.conexao import obter_caminho_banco, obter_conexao
from src.infraestrutura.schema import criar_tabelas
from src.repositorios.sqlite.cliente_repositorio_sqlite import ClienteRepositorioSQLite
from src.repositorios.sqlite.orcamento_repositorio_sqlite import OrcamentoRepositorioSQLite
from src.repositorios.sqlite.pedido_venda_repositorio_sqlite import PedidoVendaRepositorioSQLite
from src.repositorios.sqlite.tabela_preco_repositorio_sqlite import TabelaPrecoRepositorioSQLite

CPF_VALIDO = "529.982.247-25"


@pytest.fixture
def contexto(monkeypatch):
    """Prepara Cliente, TabelaPreco e Orcamento reais no banco, já que PedidoVenda
    tem chaves estrangeiras validadas pelo SQLite (PRAGMA foreign_keys = ON)."""
    monkeypatch.setenv("AMBIENTE", "teste")
    caminho = obter_caminho_banco()
    Path(caminho).unlink(missing_ok=True)

    conexao = obter_conexao()
    criar_tabelas(conexao)

    cliente = ClienteRepositorioSQLite(conexao).salvar(
        Cliente(
            nome="Cliente Teste", tipo_pessoa=TipoPessoa.FISICA, documento=CPF_VALIDO,
            email="teste@email.com", telefone="31900000000",
        )
    )
    tabela = TabelaPrecoRepositorioSQLite(conexao).salvar(TabelaPreco(nome="Varejo"))
    orcamento = OrcamentoRepositorioSQLite(conexao).salvar(
        Orcamento(cliente_id=cliente.id, tabela_preco_id=tabela.id, data_validade=date.today() + timedelta(days=15))
    )

    repo_pedido = PedidoVendaRepositorioSQLite(conexao)

    yield repo_pedido, cliente.id, orcamento.id

    conexao.close()
    Path(caminho).unlink(missing_ok=True)


def _criar_item():
    return ItemPedidoVenda(
        tipo_item=TipoItem.PRODUTO, referencia_id=1, descricao="Parafuso",
        preco_unitario=Decimal("5.00"), quantidade=Decimal("10"),
    )


def test_salvar_pedido_com_itens_persiste_todos(contexto):
    repositorio, cliente_id, orcamento_id = contexto
    pedido = repositorio.salvar(
        PedidoVenda(orcamento_id=orcamento_id, cliente_id=cliente_id, itens=[_criar_item()])
    )
    assert pedido.id is not None

    recarregado = repositorio.buscar_por_id(pedido.id)
    assert len(recarregado.itens) == 1
    assert recarregado.calcular_total() == Decimal("50.00")


def test_buscar_por_orcamento_id(contexto):
    repositorio, cliente_id, orcamento_id = contexto
    repositorio.salvar(PedidoVenda(orcamento_id=orcamento_id, cliente_id=cliente_id, itens=[_criar_item()]))

    encontrado = repositorio.buscar_por_orcamento_id(orcamento_id)
    assert encontrado is not None


def test_buscar_por_orcamento_id_inexistente_retorna_none(contexto):
    repositorio, _, _ = contexto
    assert repositorio.buscar_por_orcamento_id(9999) is None


def test_atualizar_status_e_persistido(contexto):
    repositorio, cliente_id, orcamento_id = contexto
    pedido = repositorio.salvar(
        PedidoVenda(orcamento_id=orcamento_id, cliente_id=cliente_id, itens=[_criar_item()])
    )
    pedido.avancar_para_em_separacao()
    repositorio.atualizar(pedido)

    recarregado = repositorio.buscar_por_id(pedido.id)
    assert recarregado.status == StatusPedidoVenda.EM_SEPARACAO


def test_listar_por_cliente(contexto):
    repositorio, cliente_id, orcamento_id = contexto
    repositorio.salvar(PedidoVenda(orcamento_id=orcamento_id, cliente_id=cliente_id, itens=[_criar_item()]))

    pedidos = repositorio.listar_por_cliente(cliente_id)
    assert len(pedidos) == 1


def test_listar_todos_nao_carrega_itens(contexto):
    repositorio, cliente_id, orcamento_id = contexto
    repositorio.salvar(PedidoVenda(orcamento_id=orcamento_id, cliente_id=cliente_id, itens=[_criar_item()]))

    listados = repositorio.listar_todos()
    assert len(listados) == 1
    assert listados[0].itens == []