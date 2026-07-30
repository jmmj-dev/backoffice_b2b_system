"""Testes de integração do ServicoRepositorioSQLite."""
from decimal import Decimal
from pathlib import Path

import pytest

from src.dominio.entidades.servico import Servico
from src.infraestrutura.conexao import obter_caminho_banco, obter_conexao
from src.infraestrutura.schema import criar_tabelas
from src.repositorios.sqlite.servico_repositorio_sqlite import ServicoRepositorioSQLite


@pytest.fixture
def repositorio(monkeypatch):
    monkeypatch.setenv("AMBIENTE", "teste")
    caminho = obter_caminho_banco()
    Path(caminho).unlink(missing_ok=True)
    conexao = obter_conexao()
    criar_tabelas(conexao)
    repo = ServicoRepositorioSQLite(conexao)
    yield repo
    conexao.close()
    Path(caminho).unlink(missing_ok=True)


def test_salvar_servico_gera_id(repositorio):
    servico = Servico(nome="Consultoria", valor_hora=Decimal("150"), horas_estimadas=Decimal("10"))
    salvo = repositorio.salvar(servico)
    assert salvo.id is not None


def test_buscar_por_id_preserva_precisao_decimal(repositorio):
    servico = repositorio.salvar(
        Servico(nome="Consultoria", valor_hora=Decimal("149.99"), horas_estimadas=Decimal("8"))
    )
    encontrado = repositorio.buscar_por_id(servico.id)
    assert encontrado.valor_hora == Decimal("149.99")


def test_listar_ativos_exclui_inativos(repositorio):
    ativo = repositorio.salvar(Servico(nome="Ativo", valor_hora=Decimal("100"), horas_estimadas=Decimal("1")))
    inativo = repositorio.salvar(Servico(nome="Inativo", valor_hora=Decimal("100"), horas_estimadas=Decimal("1")))
    inativo.inativar()
    repositorio.atualizar(inativo)

    assert len(repositorio.listar_ativos()) == 1
    assert len(repositorio.listar_todos()) == 2


def test_atualizar_persiste_mudancas(repositorio):
    servico = repositorio.salvar(Servico(nome="Item", valor_hora=Decimal("100"), horas_estimadas=Decimal("5")))
    servico.horas_estimadas = Decimal("8")
    repositorio.atualizar(servico)
    recarregado = repositorio.buscar_por_id(servico.id)
    assert recarregado.horas_estimadas == Decimal("8")