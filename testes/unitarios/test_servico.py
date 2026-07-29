"""Testes da entidade Servico."""
from decimal import Decimal

import pytest

from src.dominio.entidades.servico import Servico


def test_cria_servico_valido():
    servico = Servico(
        nome="Consultoria de TI",
        valor_hora=Decimal("150.00"),
        horas_estimadas=Decimal("10"),
    )
    assert servico.ativo is True


def test_valor_hora_zero_lanca_erro():
    with pytest.raises(ValueError, match="Valor por hora"):
        Servico(nome="Serviço", valor_hora=Decimal("0"), horas_estimadas=Decimal("5"))


def test_horas_estimadas_zero_lanca_erro():
    with pytest.raises(ValueError, match="Horas estimadas"):
        Servico(nome="Serviço", valor_hora=Decimal("100"), horas_estimadas=Decimal("0"))


def test_nome_vazio_lanca_erro():
    with pytest.raises(ValueError, match="Nome"):
        Servico(nome="", valor_hora=Decimal("100"), horas_estimadas=Decimal("5"))


def test_calcular_valor_total_estimado():
    servico = Servico(
        nome="Consultoria",
        valor_hora=Decimal("150.00"),
        horas_estimadas=Decimal("8"),
    )
    assert servico.calcular_valor_total_estimado() == Decimal("1200.00")


def test_valor_hora_formatado():
    servico = Servico(
        nome="Consultoria",
        valor_hora=Decimal("1234.56"),
        horas_estimadas=Decimal("1"),
    )
    assert servico.valor_hora_formatado() == "R$ 1.234,56"


def test_inativar_e_reativar_servico():
    servico = Servico(nome="Serviço", valor_hora=Decimal("100"), horas_estimadas=Decimal("2"))
    servico.inativar()
    assert servico.ativo is False
    servico.reativar()
    assert servico.ativo is True