"""Testes da entidade Produto."""
from decimal import Decimal

import pytest

from src.dominio.entidades.produto import Produto, UnidadeMedida


def test_cria_produto_valido():
    produto = Produto(
        nome="Parafuso Sextavado",
        unidade_medida=UnidadeMedida.CAIXA,
        preco_unitario=Decimal("15.90"),
    )
    assert produto.ativo is True
    assert produto.preco_unitario == Decimal("15.90")


def test_preco_zero_lanca_erro():
    with pytest.raises(ValueError, match="Preço unitário"):
        Produto(nome="Item", unidade_medida=UnidadeMedida.UNIDADE, preco_unitario=Decimal("0"))


def test_preco_negativo_lanca_erro():
    with pytest.raises(ValueError, match="Preço unitário"):
        Produto(nome="Item", unidade_medida=UnidadeMedida.UNIDADE, preco_unitario=Decimal("-5"))


def test_nome_vazio_lanca_erro():
    with pytest.raises(ValueError, match="Nome"):
        Produto(nome="  ", unidade_medida=UnidadeMedida.UNIDADE, preco_unitario=Decimal("10"))


def test_preco_formatado():
    produto = Produto(
        nome="Caixa de Parafusos",
        unidade_medida=UnidadeMedida.CAIXA,
        preco_unitario=Decimal("1234.56"),
    )
    assert produto.preco_formatado() == "R$ 1.234,56"


def test_calcular_subtotal():
    produto = Produto(
        nome="Parafuso", unidade_medida=UnidadeMedida.UNIDADE, preco_unitario=Decimal("2.50")
    )
    assert produto.calcular_subtotal(Decimal("10")) == Decimal("25.00")


def test_calcular_subtotal_quantidade_invalida_lanca_erro():
    produto = Produto(
        nome="Parafuso", unidade_medida=UnidadeMedida.UNIDADE, preco_unitario=Decimal("2.50")
    )
    with pytest.raises(ValueError, match="Quantidade"):
        produto.calcular_subtotal(Decimal("0"))


def test_inativar_e_reativar_produto():
    produto = Produto(
        nome="Item", unidade_medida=UnidadeMedida.UNIDADE, preco_unitario=Decimal("10")
    )
    produto.inativar()
    assert produto.ativo is False
    produto.reativar()
    assert produto.ativo is True