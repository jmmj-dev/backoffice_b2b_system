"""Testes do comportamento de associação de Cliente a TabelaPreco."""
from src.dominio.entidades.cliente import Cliente, TipoPessoa

CPF_VALIDO = "529.982.247-25"


def test_cliente_criado_sem_tabela_preco():
    cliente = Cliente(
        nome="Maria",
        tipo_pessoa=TipoPessoa.FISICA,
        documento=CPF_VALIDO,
        email="maria@email.com",
        telefone="31900000000",
    )
    assert cliente.tabela_preco_id is None


def test_associar_tabela_preco():
    cliente = Cliente(
        nome="Maria",
        tipo_pessoa=TipoPessoa.FISICA,
        documento=CPF_VALIDO,
        email="maria@email.com",
        telefone="31900000000",
    )
    cliente.associar_tabela_preco(3)
    assert cliente.tabela_preco_id == 3


def test_remover_tabela_preco():
    cliente = Cliente(
        nome="Maria",
        tipo_pessoa=TipoPessoa.FISICA,
        documento=CPF_VALIDO,
        email="maria@email.com",
        telefone="31900000000",
    )
    cliente.associar_tabela_preco(3)
    cliente.remover_tabela_preco()
    assert cliente.tabela_preco_id is None