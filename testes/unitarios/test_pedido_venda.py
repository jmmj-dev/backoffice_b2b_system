"""Testes da entidade PedidoVenda e sua máquina de estados de fulfillment."""
from decimal import Decimal

import pytest

from src.dominio.entidades.pedido_venda import ItemPedidoVenda, PedidoVenda, StatusPedidoVenda
from src.dominio.entidades.tabela_preco import TipoItem


def _criar_item(preco="10.00", quantidade="2"):
    return ItemPedidoVenda(
        tipo_item=TipoItem.PRODUTO,
        referencia_id=1,
        descricao="Parafuso",
        preco_unitario=Decimal(preco),
        quantidade=Decimal(quantidade),
    )


def _criar_pedido():
    return PedidoVenda(orcamento_id=1, cliente_id=1, itens=[_criar_item()])


def test_criar_pedido_valido():
    pedido = _criar_pedido()
    assert pedido.status == StatusPedidoVenda.PENDENTE
    assert pedido.calcular_total() == Decimal("20.00")



def test_fluxo_completo_ate_entregue():
    pedido = _criar_pedido()
    pedido.avancar_para_em_separacao()
    assert pedido.status == StatusPedidoVenda.EM_SEPARACAO

    pedido.faturar()
    assert pedido.status == StatusPedidoVenda.FATURADO

    pedido.marcar_como_entregue()
    assert pedido.status == StatusPedidoVenda.ENTREGUE


def test_pular_etapa_lanca_erro():
    pedido = _criar_pedido()
    with pytest.raises(ValueError, match="Não é possível mudar"):
        pedido.faturar()  # tentando pular direto de PENDENTE para FATURADO


def test_cancelar_a_partir_de_pendente():
    pedido = _criar_pedido()
    pedido.cancelar()
    assert pedido.status == StatusPedidoVenda.CANCELADO


def test_cancelar_a_partir_de_em_separacao():
    pedido = _criar_pedido()
    pedido.avancar_para_em_separacao()
    pedido.cancelar()
    assert pedido.status == StatusPedidoVenda.CANCELADO


def test_cancelar_a_partir_de_faturado():
    pedido = _criar_pedido()
    pedido.avancar_para_em_separacao()
    pedido.faturar()
    pedido.cancelar()
    assert pedido.status == StatusPedidoVenda.CANCELADO


def test_nao_pode_cancelar_pedido_entregue():
    pedido = _criar_pedido()
    pedido.avancar_para_em_separacao()
    pedido.faturar()
    pedido.marcar_como_entregue()
    with pytest.raises(ValueError, match="Não é possível mudar"):
        pedido.cancelar()


def test_nao_pode_transicionar_pedido_cancelado():
    pedido = _criar_pedido()
    pedido.cancelar()
    with pytest.raises(ValueError, match="Não é possível mudar"):
        pedido.avancar_para_em_separacao()


def test_calcular_total_com_multiplos_itens():
    pedido = PedidoVenda(
        orcamento_id=1,
        cliente_id=1,
        itens=[_criar_item(preco="10.00", quantidade="2"), _criar_item(preco="5.00", quantidade="3")],
    )
    assert pedido.calcular_total() == Decimal("35.00")