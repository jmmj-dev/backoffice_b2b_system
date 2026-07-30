"""Testes do ServicoProduto, usando repositório fake em memória."""
from decimal import Decimal

import pytest

from src.dominio.entidades.produto import Produto, UnidadeMedida
from src.servicos.servico_produto import ServicoProduto
from testes.fakes.produto_repositorio_fake import ProdutoRepositorioFake


@pytest.fixture
def servico():
    return ServicoProduto(ProdutoRepositorioFake())


def _criar_produto(nome="Parafuso", preco=Decimal("10.00")):
    return Produto(nome=nome, unidade_medida=UnidadeMedida.UNIDADE, preco_unitario=preco)


def test_criar_produto_com_sucesso(servico):
    produto = servico.criar_produto(_criar_produto())
    assert produto.id is not None


def test_atualizar_produto_sem_id_lanca_erro(servico):
    with pytest.raises(ValueError, match="sem id"):
        servico.atualizar_produto(_criar_produto())


def test_atualizar_produto_inexistente_lanca_erro(servico):
    produto = _criar_produto()
    produto.id = 999
    with pytest.raises(ValueError, match="não encontrado"):
        servico.atualizar_produto(produto)


def test_atualizar_produto_com_sucesso(servico):
    produto = servico.criar_produto(_criar_produto())
    produto.preco_unitario = Decimal("15.00")
    atualizado = servico.atualizar_produto(produto)
    assert atualizado.preco_unitario == Decimal("15.00")


def test_inativar_e_reativar_produto(servico):
    produto = servico.criar_produto(_criar_produto())
    inativado = servico.inativar_produto(produto.id)
    assert inativado.ativo is False
    reativado = servico.reativar_produto(produto.id)
    assert reativado.ativo is True


def test_listar_produtos_ativos_exclui_inativos(servico):
    p1 = servico.criar_produto(_criar_produto(nome="Um"))
    p2 = servico.criar_produto(_criar_produto(nome="Dois"))
    servico.inativar_produto(p2.id)

    assert len(servico.listar_produtos_ativos()) == 1
    assert len(servico.listar_todos_os_produtos()) == 2