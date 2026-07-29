"""Testes da entidade Cliente e suas regras de validação."""
import pytest

from src.dominio.entidades.cliente import Cliente, TipoPessoa


CPF_VALIDO = "529.982.247-25"
CNPJ_VALIDO = "11.222.333/0001-81"


def test_cria_cliente_pessoa_fisica_valido():
    cliente = Cliente(
        nome="Maria Souza",
        tipo_pessoa=TipoPessoa.FISICA,
        documento=CPF_VALIDO,
        email="maria@email.com",
        telefone="31999999999",
    )
    assert cliente.documento == "52998224725"
    assert cliente.ativo is True


def test_cria_cliente_pessoa_juridica_valido():
    cliente = Cliente(
        nome="Empresa XYZ Ltda",
        tipo_pessoa=TipoPessoa.JURIDICA,
        documento=CNPJ_VALIDO,
        email="contato@xyz.com",
        telefone="31988888888",
    )
    assert cliente.documento == "11222333000181"


def test_cpf_invalido_lanca_erro():
    with pytest.raises(ValueError, match="CPF inválido"):
        Cliente(
            nome="João",
            tipo_pessoa=TipoPessoa.FISICA,
            documento="111.111.111-11",
            email="joao@email.com",
            telefone="31900000000",
        )


def test_cnpj_invalido_lanca_erro():
    with pytest.raises(ValueError, match="CNPJ inválido"):
        Cliente(
            nome="Empresa Falsa",
            tipo_pessoa=TipoPessoa.JURIDICA,
            documento="00.000.000/0000-00",
            email="falsa@email.com",
            telefone="31900000000",
        )


def test_nome_vazio_lanca_erro():
    with pytest.raises(ValueError, match="Nome"):
        Cliente(
            nome="   ",
            tipo_pessoa=TipoPessoa.FISICA,
            documento=CPF_VALIDO,
            email="teste@email.com",
            telefone="31900000000",
        )


def test_email_invalido_lanca_erro():
    with pytest.raises(ValueError, match="E-mail inválido"):
        Cliente(
            nome="Carlos",
            tipo_pessoa=TipoPessoa.FISICA,
            documento=CPF_VALIDO,
            email="email-sem-arroba",
            telefone="31900000000",
        )


def test_inativar_e_reativar_cliente():
    cliente = Cliente(
        nome="Ana",
        tipo_pessoa=TipoPessoa.FISICA,
        documento=CPF_VALIDO,
        email="ana@email.com",
        telefone="31900000000",
    )
    cliente.inativar()
    assert cliente.ativo is False
    cliente.reativar()
    assert cliente.ativo is True


def test_documento_formatado_cpf():
    cliente = Cliente(
        nome="Maria",
        tipo_pessoa=TipoPessoa.FISICA,
        documento=CPF_VALIDO,
        email="maria@email.com",
        telefone="31900000000",
    )
    assert cliente.documento_formatado() == "529.982.247-25"


def test_documento_formatado_cnpj():
    cliente = Cliente(
        nome="Empresa XYZ",
        tipo_pessoa=TipoPessoa.JURIDICA,
        documento=CNPJ_VALIDO,
        email="contato@xyz.com",
        telefone="31900000000",
    )
    assert cliente.documento_formatado() == "11.222.333/0001-81"