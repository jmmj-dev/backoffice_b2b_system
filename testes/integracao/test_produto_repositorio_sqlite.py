"""Testes de integração do ProdutoRepositorioSQLite."""
from decimal import Decimal
from pathlib import Path

import pytest

from src.dominio.entidades.produto import Produto, UnidadeMedida
from src.infraestrutura.conexao import obter_caminho_banco, obter_conexao
from src.infraestrutura.schema import criar_tabelas
from src.repositorios.sqlite.produto_repositorio_sqlite import ProdutoRepositorioSQLite


@pytest.fixture
def repositorio(monkeypatch):
    monkeypatch.setenv("AMBIENTE", "teste")
    caminho = obter_caminho_banco()
    Path(caminho).unlink(missing_ok=True)
    conexao = obter_conexao()
    criar_tabelas(conexao)
    repo = ProdutoRepositorioSQLite(conexao)
    yield repo
    conexao.close()
    Path(caminho).unlink(missing_ok=True)


def test_salvar_produto_gera_id(repositorio):
    produto = Produto(nome="Parafuso", unidade_medida=UnidadeMedida.CAIXA, preco_unitario=Decimal("15.90"))
    salvo = repositorio.salvar(produto)
    assert salvo.id is not None


def test_buscar_por_id_preserva_precisao_decimal(repositorio):
    produto = repositorio.salvar(
        Produto(nome="Item", unidade_medida=UnidadeMedida.UNIDADE, preco_unitario=Decimal("19.99"))
    )
    encontrado = repositorio.buscar_por_id(produto.id)
    assert encontrado.preco_unitario == Decimal("19.99")


def test_listar_ativos_exclui_inativos(repositorio):
    ativo = repositorio.salvar(
        Produto(nome="Ativo", unidade_medida=UnidadeMedida.UNIDADE, preco_unitario=Decimal("10"))
    )
    inativo = repositorio.salvar(
        Produto(nome="Inativo", unidade_medida=UnidadeMedida.UNIDADE, preco_unitario=Decimal("10"))
    )
    inativo.inativar()
    repositorio.atualizar(inativo)

    assert len(repositorio.listar_ativos()) == 1
    assert len(repositorio.listar_todos()) == 2


def test_atualizar_persiste_mudancas(repositorio):
    produto = repositorio.salvar(
        Produto(nome="Item", unidade_medida=UnidadeMedida.UNIDADE, preco_unitario=Decimal("10"))
    )
    produto.preco_unitario = Decimal("12.50")
    repositorio.atualizar(produto)
    recarregado = repositorio.buscar_por_id(produto.id)
    assert recarregado.preco_unitario == Decimal("12.50")