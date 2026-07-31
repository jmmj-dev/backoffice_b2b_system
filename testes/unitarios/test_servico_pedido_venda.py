"""Testes do ServicoPedidoVenda, cobrindo a criação a partir de orçamento aceito e a
máquina de estados de fulfillment."""
from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.dominio.entidades.orcamento import Orcamento
from src.dominio.entidades.pedido_venda import StatusPedidoVenda
from src.dominio.entidades.tabela_preco import TipoItem
from src.servicos.servico_pedido_venda import ServicoPedidoVenda
from testes.fakes.orcamento_repositorio_fake import OrcamentoRepositorioFake
from testes.fakes.pedido_venda_repositorio_fake import PedidoVendaRepositorioFake


@pytest.fixture
def contexto():
    repo_orcamento = OrcamentoRepositorioFake()
    repo_pedido = PedidoVendaRepositorioFake()
    servico = ServicoPedidoVenda(repo_pedido, repo_orcamento)
    return servico, repo_orcamento


def _criar_orcamento_aceito(repo_orcamento, com_itens=True):
    orcamento = Orcamento(cliente_id=1, tabela_preco_id=1, data_validade=date.today() + timedelta(days=15))
    if com_itens:
        orcamento.adicionar_item(
            TipoItem.PRODUTO, referencia_id=1, descricao="Parafuso", preco_unitario=Decimal("5.00"), quantidade=Decimal("10")
        )
    if com_itens:
        orcamento.enviar()
        orcamento.aceitar()
    orcamento = repo_orcamento.salvar(orcamento)
    return orcamento


def test_criar_pedido_a_partir_de_orcamento_aceito(contexto):
    servico, repo_orcamento = contexto
    orcamento = _criar_orcamento_aceito(repo_orcamento)

    pedido = servico.criar_a_partir_de_orcamento(orcamento.id)
    assert pedido.id is not None
    assert pedido.status == StatusPedidoVenda.PENDENTE
    assert pedido.calcular_total() == Decimal("50.00")


def test_criar_pedido_de_orcamento_nao_aceito_lanca_erro(contexto):
    servico, repo_orcamento = contexto
    orcamento = Orcamento(cliente_id=1, tabela_preco_id=1, data_validade=date.today() + timedelta(days=15))
    orcamento = repo_orcamento.salvar(orcamento)  # ainda em RASCUNHO

    with pytest.raises(ValueError, match="ACEITO"):
        servico.criar_a_partir_de_orcamento(orcamento.id)


def test_criar_pedido_duplicado_lanca_erro(contexto):
    servico, repo_orcamento = contexto
    orcamento = _criar_orcamento_aceito(repo_orcamento)
    servico.criar_a_partir_de_orcamento(orcamento.id)

    with pytest.raises(ValueError, match="já gerou o pedido"):
        servico.criar_a_partir_de_orcamento(orcamento.id)


def test_criar_pedido_orcamento_inexistente_lanca_erro(contexto):
    servico, _ = contexto
    with pytest.raises(ValueError, match="não encontrado"):
        servico.criar_a_partir_de_orcamento(9999)


def test_fluxo_completo_de_fulfillment(contexto):
    servico, repo_orcamento = contexto
    orcamento = _criar_orcamento_aceito(repo_orcamento)
    pedido = servico.criar_a_partir_de_orcamento(orcamento.id)

    servico.avancar_para_em_separacao(pedido.id)
    servico.faturar(pedido.id)
    entregue = servico.marcar_como_entregue(pedido.id)

    assert entregue.status == StatusPedidoVenda.ENTREGUE


def test_cancelar_pedido(contexto):
    servico, repo_orcamento = contexto
    orcamento = _criar_orcamento_aceito(repo_orcamento)
    pedido = servico.criar_a_partir_de_orcamento(orcamento.id)

    cancelado = servico.cancelar(pedido.id)
    assert cancelado.status == StatusPedidoVenda.CANCELADO


def test_listar_por_cliente(contexto):
    servico, repo_orcamento = contexto
    orcamento = _criar_orcamento_aceito(repo_orcamento)
    servico.criar_a_partir_de_orcamento(orcamento.id)

    pedidos = servico.listar_por_cliente(1)
    assert len(pedidos) == 1