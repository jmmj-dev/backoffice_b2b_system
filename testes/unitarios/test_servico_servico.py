"""Testes do ServicoServico, usando repositório fake em memória."""
from decimal import Decimal

import pytest

from src.dominio.entidades.servico import Servico
from src.servicos.servico_servico import ServicoServico
from testes.fakes.servico_repositorio_fake import ServicoRepositorioFake


@pytest.fixture
def servico_de_servico():
    return ServicoServico(ServicoRepositorioFake())


def _criar_servico(nome="Consultoria", valor_hora=Decimal("100.00")):
    return Servico(nome=nome, valor_hora=valor_hora, horas_estimadas=Decimal("5"))


def test_criar_servico_com_sucesso(servico_de_servico):
    servico = servico_de_servico.criar_servico(_criar_servico())
    assert servico.id is not None


def test_atualizar_servico_sem_id_lanca_erro(servico_de_servico):
    with pytest.raises(ValueError, match="sem id"):
        servico_de_servico.atualizar_servico(_criar_servico())


def test_atualizar_servico_inexistente_lanca_erro(servico_de_servico):
    servico = _criar_servico()
    servico.id = 999
    with pytest.raises(ValueError, match="não encontrado"):
        servico_de_servico.atualizar_servico(servico)


def test_inativar_e_reativar_servico(servico_de_servico):
    servico = servico_de_servico.criar_servico(_criar_servico())
    inativado = servico_de_servico.inativar_servico(servico.id)
    assert inativado.ativo is False
    reativado = servico_de_servico.reativar_servico(servico.id)
    assert reativado.ativo is True


def test_listar_servicos_ativos_exclui_inativos(servico_de_servico):
    s1 = servico_de_servico.criar_servico(_criar_servico(nome="Um"))
    s2 = servico_de_servico.criar_servico(_criar_servico(nome="Dois"))
    servico_de_servico.inativar_servico(s2.id)

    assert len(servico_de_servico.listar_servicos_ativos()) == 1
    assert len(servico_de_servico.listar_todos_os_servicos()) == 2