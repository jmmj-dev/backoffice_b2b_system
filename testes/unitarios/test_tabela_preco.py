"""Testes da entidade TabelaPreco e ItemTabelaPreco."""
from decimal import Decimal

import pytest

from src.dominio.entidades.tabela_preco import TabelaPreco, TipoItem


def test_cria_tabela_preco_valida():
    tabela = TabelaPreco(nome="Varejo")
    assert tabela.ativa is True
    assert tabela.itens == []


def test_nome_vazio_lanca_erro():
    with pytest.raises(ValueError, match="Nome da tabela"):
        TabelaPreco(nome="")


def test_adicionar_item_produto():
    tabela = TabelaPreco(nome="Varejo")
    item = tabela.adicionar_item(TipoItem.PRODUTO, referencia_id=1, preco=Decimal("50.00"))
    assert item.preco == Decimal("50.00")
    assert len(tabela.itens) == 1


def test_adicionar_item_duplicado_lanca_erro():
    tabela = TabelaPreco(nome="Varejo")
    tabela.adicionar_item(TipoItem.PRODUTO, referencia_id=1, preco=Decimal("50.00"))
    with pytest.raises(ValueError, match="Já existe"):
        tabela.adicionar_item(TipoItem.PRODUTO, referencia_id=1, preco=Decimal("60.00"))


def test_adicionar_item_preco_invalido_lanca_erro():
    tabela = TabelaPreco(nome="Varejo")
    with pytest.raises(ValueError, match="Preço do item"):
        tabela.adicionar_item(TipoItem.PRODUTO, referencia_id=1, preco=Decimal("0"))


def test_obter_preco_existente():
    tabela = TabelaPreco(nome="Varejo")
    tabela.adicionar_item(TipoItem.SERVICO, referencia_id=5, preco=Decimal("200.00"))
    assert tabela.obter_preco(TipoItem.SERVICO, referencia_id=5) == Decimal("200.00")


def test_obter_preco_inexistente_retorna_none():
    tabela = TabelaPreco(nome="Varejo")
    assert tabela.obter_preco(TipoItem.PRODUTO, referencia_id=99) is None


def test_atualizar_preco_item():
    tabela = TabelaPreco(nome="Varejo")
    tabela.adicionar_item(TipoItem.PRODUTO, referencia_id=1, preco=Decimal("50.00"))
    tabela.atualizar_preco_item(TipoItem.PRODUTO, referencia_id=1, novo_preco=Decimal("55.00"))
    assert tabela.obter_preco(TipoItem.PRODUTO, referencia_id=1) == Decimal("55.00")


def test_atualizar_preco_item_inexistente_lanca_erro():
    tabela = TabelaPreco(nome="Varejo")
    with pytest.raises(ValueError, match="Nenhum item ativo"):
        tabela.atualizar_preco_item(TipoItem.PRODUTO, referencia_id=1, novo_preco=Decimal("10"))


def test_remover_item_soft_delete():
    tabela = TabelaPreco(nome="Varejo")
    tabela.adicionar_item(TipoItem.PRODUTO, referencia_id=1, preco=Decimal("50.00"))
    tabela.remover_item(TipoItem.PRODUTO, referencia_id=1)
    assert tabela.obter_preco(TipoItem.PRODUTO, referencia_id=1) is None
    assert len(tabela.itens) == 1  # item continua existindo, só inativo
    assert tabela.itens[0].ativo is False


def test_pode_readicionar_item_apos_remocao():
    """Depois de remover (soft delete) um item, deve ser possível adicioná-lo de novo."""
    tabela = TabelaPreco(nome="Varejo")
    tabela.adicionar_item(TipoItem.PRODUTO, referencia_id=1, preco=Decimal("50.00"))
    tabela.remover_item(TipoItem.PRODUTO, referencia_id=1)
    novo_item = tabela.adicionar_item(TipoItem.PRODUTO, referencia_id=1, preco=Decimal("60.00"))
    assert novo_item.preco == Decimal("60.00")


def test_inativar_e_reativar_tabela():
    tabela = TabelaPreco(nome="Varejo")
    tabela.inativar()
    assert tabela.ativa is False
    tabela.reativar()
    assert tabela.ativa is True