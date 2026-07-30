"""Testes do ServicoOrcamento, cobrindo resolução de preço via tabela e o fluxo de status."""
from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.dominio.entidades.cliente import Cliente, TipoPessoa
from src.dominio.entidades.orcamento import StatusOrcamento
from src.dominio.entidades.produto import Produto, UnidadeMedida
from src.dominio.entidades.tabela_preco import TabelaPreco, TipoItem
from src.servicos.servico_orcamento import ServicoOrcamento
from testes.fakes.cliente_repositorio_fake import ClienteRepositorioFake
from testes.fakes.orcamento_repositorio_fake import OrcamentoRepositorioFake
from testes.fakes.produto_repositorio_fake import ProdutoRepositorioFake
from testes.fakes.servico_repositorio_fake import ServicoRepositorioFake
from testes.fakes.tabela_preco_repositorio_fake import TabelaPrecoRepositorioFake

CPF_VALIDO = "529.982.247-25"


@pytest.fixture
def contexto():
    """Monta o ServicoOrcamento com todos os fakes, já com um cliente (associado a uma tabela)
    e um produto precificado naquela tabela."""
    repo_cliente = ClienteRepositorioFake()
    repo_tabela = TabelaPrecoRepositorioFake()
    repo_produto = ProdutoRepositorioFake()
    repo_servico = ServicoRepositorioFake()
    repo_orcamento = OrcamentoRepositorioFake()

    produto = repo_produto.salvar(
        Produto(nome="Parafuso", unidade_medida=UnidadeMedida.UNIDADE, preco_unitario=Decimal("5.00"))
    )

    tabela = TabelaPreco(nome="Varejo")
    tabela.adicionar_item(TipoItem.PRODUTO, produto.id, Decimal("6.00"))
    tabela = repo_tabela.salvar(tabela)

    cliente = Cliente(
        nome="Cliente Teste", tipo_pessoa=TipoPessoa.FISICA, documento=CPF_VALIDO,
        email="teste@email.com", telefone="31900000000",
    )
    cliente.associar_tabela_preco(tabela.id)
    cliente = repo_cliente.salvar(cliente)

    servico = ServicoOrcamento(repo_orcamento, repo_cliente, repo_tabela, repo_produto, repo_servico)
    return servico, cliente, produto, tabela, repo_cliente


def test_criar_orcamento_usa_tabela_do_cliente_automaticamente(contexto):
    servico, cliente, _, tabela, _ = contexto
    orcamento = servico.criar_orcamento(cliente.id, data_validade=date.today() + timedelta(days=15))
    assert orcamento.tabela_preco_id == tabela.id


def test_criar_orcamento_cliente_sem_tabela_lanca_erro(contexto):
    servico, cliente, _, _, repo_cliente = contexto
    cliente.remover_tabela_preco()
    repo_cliente.atualizar(cliente)

    with pytest.raises(ValueError, match="não possui tabela de preço"):
        servico.criar_orcamento(cliente.id, data_validade=date.today() + timedelta(days=15))


def test_criar_orcamento_cliente_inativo_lanca_erro(contexto):
    servico, cliente, _, _, repo_cliente = contexto
    cliente.inativar()
    repo_cliente.atualizar(cliente)

    with pytest.raises(ValueError, match="está inativo"):
        servico.criar_orcamento(cliente.id, data_validade=date.today() + timedelta(days=15))


def test_adicionar_item_resolve_preco_da_tabela(contexto):
    servico, cliente, produto, _, _ = contexto
    orcamento = servico.criar_orcamento(cliente.id, data_validade=date.today() + timedelta(days=15))

    item = servico.adicionar_item(orcamento.id, TipoItem.PRODUTO, produto.id, Decimal("3"))
    assert item.preco_unitario == Decimal("6.00")
    assert item.descricao == "Parafuso"
    assert item.calcular_subtotal() == Decimal("18.00")


def test_adicionar_item_sem_preco_na_tabela_lanca_erro(contexto):
    servico, cliente, _, _, _ = contexto
    orcamento = servico.criar_orcamento(cliente.id, data_validade=date.today() + timedelta(days=15))

    with pytest.raises(ValueError, match="Não há preço cadastrado"):
        servico.adicionar_item(orcamento.id, TipoItem.PRODUTO, 9999, Decimal("1"))


def test_fluxo_completo_criar_enviar_aceitar(contexto):
    servico, cliente, produto, _, _ = contexto
    orcamento = servico.criar_orcamento(cliente.id, data_validade=date.today() + timedelta(days=15))
    servico.adicionar_item(orcamento.id, TipoItem.PRODUTO, produto.id, Decimal("2"))

    servico.enviar_orcamento(orcamento.id)
    aceito = servico.aceitar_orcamento(orcamento.id)

    assert aceito.status == StatusOrcamento.ACEITO


def test_aplicar_desconto_via_servico(contexto):
    servico, cliente, produto, _, _ = contexto
    orcamento = servico.criar_orcamento(cliente.id, data_validade=date.today() + timedelta(days=15))
    servico.adicionar_item(orcamento.id, TipoItem.PRODUTO, produto.id, Decimal("10"))

    atualizado = servico.aplicar_desconto(orcamento.id, Decimal("10"))
    assert atualizado.calcular_total() == Decimal("54.00")  # 60.00 - 10%


def test_aceitar_orcamento_expirado_verifica_e_bloqueia(contexto):
    servico, cliente, produto, _, repo_cliente = contexto
    orcamento = servico.criar_orcamento(cliente.id, data_validade=date.today() + timedelta(days=1))
    servico.adicionar_item(orcamento.id, TipoItem.PRODUTO, produto.id, Decimal("1"))
    servico.enviar_orcamento(orcamento.id)

    # Simula passagem do tempo além da validade, persistindo a mudança no fake
    orcamento_recarregado = servico.buscar_por_id(orcamento.id)
    orcamento_recarregado.data_validade = date.today() - timedelta(days=1)
    servico._repositorio.atualizar(orcamento_recarregado)

    with pytest.raises(ValueError):
        servico.aceitar_orcamento(orcamento.id)


def test_listar_por_cliente(contexto):
    servico, cliente, _, _, _ = contexto
    servico.criar_orcamento(cliente.id, data_validade=date.today() + timedelta(days=15))
    orcamentos = servico.listar_por_cliente(cliente.id)
    assert len(orcamentos) == 1