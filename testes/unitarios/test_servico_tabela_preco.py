"""Testes do ServicoTabelaPreco, incluindo a validação cruzada com Produto e Serviço."""
from decimal import Decimal

import pytest

from src.dominio.entidades.produto import Produto, UnidadeMedida
from src.dominio.entidades.servico import Servico
from src.dominio.entidades.tabela_preco import TabelaPreco, TipoItem
from src.servicos.servico_tabela_preco import ServicoTabelaPreco
from testes.fakes.produto_repositorio_fake import ProdutoRepositorioFake
from testes.fakes.servico_repositorio_fake import ServicoRepositorioFake
from testes.fakes.tabela_preco_repositorio_fake import TabelaPrecoRepositorioFake


@pytest.fixture
def contexto():
    """Monta o ServicoTabelaPreco com os três fakes, e já cadastra um produto e um serviço ativos."""
    repo_tabela = TabelaPrecoRepositorioFake()
    repo_produto = ProdutoRepositorioFake()
    repo_servico = ServicoRepositorioFake()

    produto = repo_produto.salvar(
        Produto(nome="Parafuso", unidade_medida=UnidadeMedida.UNIDADE, preco_unitario=Decimal("5.00"))
    )
    servico_prestado = repo_servico.salvar(
        Servico(nome="Consultoria", valor_hora=Decimal("100.00"), horas_estimadas=Decimal("2"))
    )

    servico_tabela = ServicoTabelaPreco(repo_tabela, repo_produto, repo_servico)
    return servico_tabela, produto, servico_prestado, repo_produto, repo_servico


def test_criar_tabela_com_sucesso(contexto):
    servico_tabela, _, _, _, _ = contexto
    tabela = servico_tabela.criar_tabela(TabelaPreco(nome="Varejo"))
    assert tabela.id is not None


def test_adicionar_item_produto_valido(contexto):
    servico_tabela, produto, _, _, _ = contexto
    tabela = servico_tabela.criar_tabela(TabelaPreco(nome="Varejo"))
    item = servico_tabela.adicionar_item(tabela.id, TipoItem.PRODUTO, produto.id, Decimal("6.00"))
    assert item.preco == Decimal("6.00")


def test_adicionar_item_com_produto_inexistente_lanca_erro(contexto):
    servico_tabela, _, _, _, _ = contexto
    tabela = servico_tabela.criar_tabela(TabelaPreco(nome="Varejo"))
    with pytest.raises(ValueError, match="não encontrado"):
        servico_tabela.adicionar_item(tabela.id, TipoItem.PRODUTO, 9999, Decimal("6.00"))


def test_adicionar_item_com_produto_inativo_lanca_erro(contexto):
    servico_tabela, produto, _, repo_produto, _ = contexto
    produto.inativar()
    repo_produto.atualizar(produto)

    tabela = servico_tabela.criar_tabela(TabelaPreco(nome="Varejo"))
    with pytest.raises(ValueError, match="está inativo"):
        servico_tabela.adicionar_item(tabela.id, TipoItem.PRODUTO, produto.id, Decimal("6.00"))


def test_adicionar_item_servico_valido(contexto):
    servico_tabela, _, servico_prestado, _, _ = contexto
    tabela = servico_tabela.criar_tabela(TabelaPreco(nome="Varejo"))
    item = servico_tabela.adicionar_item(
        tabela.id, TipoItem.SERVICO, servico_prestado.id, Decimal("120.00")
    )
    assert item.preco == Decimal("120.00")


def test_atualizar_preco_item_persiste(contexto):
    servico_tabela, produto, _, _, _ = contexto
    tabela = servico_tabela.criar_tabela(TabelaPreco(nome="Varejo"))
    servico_tabela.adicionar_item(tabela.id, TipoItem.PRODUTO, produto.id, Decimal("6.00"))

    servico_tabela.atualizar_preco_item(tabela.id, TipoItem.PRODUTO, produto.id, Decimal("7.50"))

    tabela_recarregada = servico_tabela.buscar_por_id(tabela.id)
    assert tabela_recarregada.obter_preco(TipoItem.PRODUTO, produto.id) == Decimal("7.50")


def test_remover_item_persiste(contexto):
    servico_tabela, produto, _, _, _ = contexto
    tabela = servico_tabela.criar_tabela(TabelaPreco(nome="Varejo"))
    servico_tabela.adicionar_item(tabela.id, TipoItem.PRODUTO, produto.id, Decimal("6.00"))

    servico_tabela.remover_item(tabela.id, TipoItem.PRODUTO, produto.id)

    tabela_recarregada = servico_tabela.buscar_por_id(tabela.id)
    assert tabela_recarregada.obter_preco(TipoItem.PRODUTO, produto.id) is None


def test_inativar_e_reativar_tabela(contexto):
    servico_tabela, _, _, _, _ = contexto
    tabela = servico_tabela.criar_tabela(TabelaPreco(nome="Varejo"))
    inativada = servico_tabela.inativar_tabela(tabela.id)
    assert inativada.ativa is False
    reativada = servico_tabela.reativar_tabela(tabela.id)
    assert reativada.ativa is True


def test_listar_tabelas_ativas_exclui_inativas(contexto):
    servico_tabela, _, _, _, _ = contexto
    t1 = servico_tabela.criar_tabela(TabelaPreco(nome="Um"))
    t2 = servico_tabela.criar_tabela(TabelaPreco(nome="Dois"))
    servico_tabela.inativar_tabela(t2.id)

    assert len(servico_tabela.listar_tabelas_ativas()) == 1
    assert len(servico_tabela.listar_todas_as_tabelas()) == 2