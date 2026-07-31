"""Testes do ServicoCliente, usando repositório fake em memória (sem tocar banco real)."""
import pytest

from testes.fakes.tabela_preco_repositorio_fake import TabelaPrecoRepositorioFake
from src.dominio.entidades.cliente import Cliente, TipoPessoa
from src.servicos.servico_cliente import ServicoCliente
from testes.fakes.cliente_repositorio_fake import ClienteRepositorioFake

CPF_VALIDO = "529.982.247-25"
CNPJ_VALIDO = "11.222.333/0001-81"


@pytest.fixture
def servico():
    return ServicoCliente(ClienteRepositorioFake(), TabelaPrecoRepositorioFake())


def _criar_cliente(documento=CPF_VALIDO, tipo=TipoPessoa.FISICA, nome="Maria"):
    return Cliente(
        nome=nome, tipo_pessoa=tipo, documento=documento, email="teste@email.com", telefone="31900000000"
    )


def test_criar_cliente_com_sucesso(servico):
    cliente = servico.criar_cliente(_criar_cliente())
    assert cliente.id is not None


def test_criar_cliente_com_documento_duplicado_ativo_lanca_erro(servico):
    servico.criar_cliente(_criar_cliente())
    with pytest.raises(ValueError, match="Já existe um cliente ativo"):
        servico.criar_cliente(_criar_cliente(nome="Outra Pessoa"))


def test_criar_cliente_com_documento_de_cliente_inativo_orienta_reativacao(servico):
    cliente = servico.criar_cliente(_criar_cliente())
    servico.inativar_cliente(cliente.id)

    with pytest.raises(ValueError, match="Reative o cliente existente"):
        servico.criar_cliente(_criar_cliente(nome="Outra Pessoa"))


def test_inativar_cliente(servico):
    cliente = servico.criar_cliente(_criar_cliente())
    inativado = servico.inativar_cliente(cliente.id)
    assert inativado.ativo is False


def test_reativar_cliente(servico):
    cliente = servico.criar_cliente(_criar_cliente())
    servico.inativar_cliente(cliente.id)
    reativado = servico.reativar_cliente(cliente.id)
    assert reativado.ativo is True


def test_inativar_cliente_inexistente_lanca_erro(servico):
    with pytest.raises(ValueError, match="não encontrado"):
        servico.inativar_cliente(9999)


def test_atualizar_cliente_com_sucesso(servico):
    cliente = servico.criar_cliente(_criar_cliente())
    cliente.telefone = "31911111111"
    atualizado = servico.atualizar_cliente(cliente)
    assert atualizado.telefone == "31911111111"


def test_atualizar_cliente_sem_id_lanca_erro(servico):
    cliente_sem_id = _criar_cliente()
    with pytest.raises(ValueError, match="sem id"):
        servico.atualizar_cliente(cliente_sem_id)


def test_atualizar_documento_para_um_ja_usado_por_outro_cliente_lanca_erro(servico):
    servico.criar_cliente(_criar_cliente(documento=CPF_VALIDO, nome="Cliente Um"))
    cliente_dois = servico.criar_cliente(
        _criar_cliente(documento="111.444.777-35", tipo=TipoPessoa.FISICA, nome="Cliente Dois")
    )
    # Simula tentativa de mudar o documento do cliente dois para o do cliente um
    cliente_dois.documento = "52998224725"
    with pytest.raises(ValueError, match="já pertence a outro cliente"):
        servico.atualizar_cliente(cliente_dois)


def test_listar_clientes_ativos_exclui_inativos(servico):
    c1 = servico.criar_cliente(_criar_cliente(documento=CPF_VALIDO, nome="Um"))
    c2 = servico.criar_cliente(_criar_cliente(documento=CNPJ_VALIDO, tipo=TipoPessoa.JURIDICA, nome="Dois"))
    servico.inativar_cliente(c2.id)

    ativos = servico.listar_clientes_ativos()
    assert len(ativos) == 1
    assert ativos[0].nome == "Um"

    todos = servico.listar_todos_os_clientes()
    assert len(todos) == 2

def test_associar_tabela_preco_valida(servico):
    from decimal import Decimal
    from src.dominio.entidades.tabela_preco import TabelaPreco

    tabela_repo = servico._tabela_preco_repositorio
    tabela = tabela_repo.salvar(TabelaPreco(nome="Varejo"))

    cliente = servico.criar_cliente(_criar_cliente())
    atualizado = servico.associar_tabela_preco(cliente.id, tabela.id)
    assert atualizado.tabela_preco_id == tabela.id


def test_associar_tabela_preco_inexistente_lanca_erro(servico):
    cliente = servico.criar_cliente(_criar_cliente())
    with pytest.raises(ValueError, match="não encontrada"):
        servico.associar_tabela_preco(cliente.id, 9999)


def test_associar_tabela_preco_inativa_lanca_erro(servico):
    from src.dominio.entidades.tabela_preco import TabelaPreco

    tabela_repo = servico._tabela_preco_repositorio
    tabela = tabela_repo.salvar(TabelaPreco(nome="Varejo"))
    tabela.inativar()
    tabela_repo.atualizar(tabela)

    cliente = servico.criar_cliente(_criar_cliente())
    with pytest.raises(ValueError, match="está inativa"):
        servico.associar_tabela_preco(cliente.id, tabela.id)    