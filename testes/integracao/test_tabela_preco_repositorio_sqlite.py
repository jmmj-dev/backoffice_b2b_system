"""Testes de integração do TabelaPrecoRepositorioSQLite, incluindo persistência dos itens (agregado)."""
from decimal import Decimal
from pathlib import Path

import pytest

from src.dominio.entidades.tabela_preco import TabelaPreco, TipoItem
from src.infraestrutura.conexao import obter_caminho_banco, obter_conexao
from src.infraestrutura.schema import criar_tabelas
from src.repositorios.sqlite.tabela_preco_repositorio_sqlite import TabelaPrecoRepositorioSQLite


@pytest.fixture
def repositorio(monkeypatch):
    monkeypatch.setenv("AMBIENTE", "teste")
    caminho = obter_caminho_banco()
    Path(caminho).unlink(missing_ok=True)
    conexao = obter_conexao()
    criar_tabelas(conexao)
    repo = TabelaPrecoRepositorioSQLite(conexao)
    yield repo
    conexao.close()
    Path(caminho).unlink(missing_ok=True)


def test_salvar_tabela_sem_itens(repositorio):
    tabela = repositorio.salvar(TabelaPreco(nome="Varejo"))
    assert tabela.id is not None


def test_salvar_tabela_com_itens_persiste_todos(repositorio):
    tabela = TabelaPreco(nome="Atacado")
    tabela.adicionar_item(TipoItem.PRODUTO, referencia_id=1, preco=Decimal("50.00"))
    tabela.adicionar_item(TipoItem.SERVICO, referencia_id=2, preco=Decimal("200.00"))
    repositorio.salvar(tabela)

    recarregada = repositorio.buscar_por_id(tabela.id)
    assert len(recarregada.itens) == 2
    assert recarregada.obter_preco(TipoItem.PRODUTO, referencia_id=1) == Decimal("50.00")


def test_buscar_por_id_carrega_itens(repositorio):
    tabela = TabelaPreco(nome="Varejo")
    tabela.adicionar_item(TipoItem.PRODUTO, referencia_id=10, preco=Decimal("99.90"))
    repositorio.salvar(tabela)

    encontrada = repositorio.buscar_por_id(tabela.id)
    assert encontrada.obter_preco(TipoItem.PRODUTO, referencia_id=10) == Decimal("99.90")


def test_listar_ativas_nao_carrega_itens(repositorio):
    tabela = TabelaPreco(nome="Varejo")
    tabela.adicionar_item(TipoItem.PRODUTO, referencia_id=1, preco=Decimal("10"))
    repositorio.salvar(tabela)

    listadas = repositorio.listar_ativas()
    assert len(listadas) == 1
    assert listadas[0].itens == []  # listagem rasa, sem itens


def test_atualizar_novo_item_e_persistido(repositorio):
    tabela = repositorio.salvar(TabelaPreco(nome="Varejo"))
    tabela.adicionar_item(TipoItem.PRODUTO, referencia_id=5, preco=Decimal("30.00"))
    repositorio.atualizar(tabela)

    recarregada = repositorio.buscar_por_id(tabela.id)
    assert recarregada.obter_preco(TipoItem.PRODUTO, referencia_id=5) == Decimal("30.00")


def test_atualizar_preco_de_item_existente_e_persistido(repositorio):
    tabela = TabelaPreco(nome="Varejo")
    tabela.adicionar_item(TipoItem.PRODUTO, referencia_id=1, preco=Decimal("50.00"))
    repositorio.salvar(tabela)

    tabela.atualizar_preco_item(TipoItem.PRODUTO, referencia_id=1, novo_preco=Decimal("60.00"))
    repositorio.atualizar(tabela)

    recarregada = repositorio.buscar_por_id(tabela.id)
    assert recarregada.obter_preco(TipoItem.PRODUTO, referencia_id=1) == Decimal("60.00")


def test_remover_item_soft_delete_e_persistido(repositorio):
    tabela = TabelaPreco(nome="Varejo")
    tabela.adicionar_item(TipoItem.PRODUTO, referencia_id=1, preco=Decimal("50.00"))
    repositorio.salvar(tabela)

    tabela.remover_item(TipoItem.PRODUTO, referencia_id=1)
    repositorio.atualizar(tabela)

    recarregada = repositorio.buscar_por_id(tabela.id)
    assert recarregada.obter_preco(TipoItem.PRODUTO, referencia_id=1) is None
    assert len(recarregada.itens) == 1  # item continua existindo, só inativo