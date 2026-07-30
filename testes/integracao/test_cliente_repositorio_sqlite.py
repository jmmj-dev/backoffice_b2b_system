"""Testes de integração do ClienteRepositorioSQLite contra um banco SQLite real e isolado."""
from pathlib import Path

import pytest

from src.dominio.entidades.cliente import Cliente, TipoPessoa
from src.infraestrutura.conexao import obter_caminho_banco, obter_conexao
from src.infraestrutura.schema import criar_tabelas
from src.repositorios.sqlite.cliente_repositorio_sqlite import ClienteRepositorioSQLite

CPF_VALIDO = "529.982.247-25"
CNPJ_VALIDO = "11.222.333/0001-81"


@pytest.fixture
def repositorio(monkeypatch):
    """Cria um repositório apontando para um banco de TESTE isolado, limpo antes e depois."""
    monkeypatch.setenv("AMBIENTE", "teste")
    caminho = obter_caminho_banco()
    Path(caminho).unlink(missing_ok=True)

    conexao = obter_conexao()
    criar_tabelas(conexao)
    repo = ClienteRepositorioSQLite(conexao)

    yield repo

    conexao.close()
    Path(caminho).unlink(missing_ok=True)


def test_salvar_cliente_gera_id(repositorio):
    cliente = Cliente(
        nome="Maria Souza",
        tipo_pessoa=TipoPessoa.FISICA,
        documento=CPF_VALIDO,
        email="maria@email.com",
        telefone="31999999999",
    )
    cliente_salvo = repositorio.salvar(cliente)
    assert cliente_salvo.id is not None


def test_buscar_por_id_encontra_cliente(repositorio):
    cliente = repositorio.salvar(
        Cliente(
            nome="Maria",
            tipo_pessoa=TipoPessoa.FISICA,
            documento=CPF_VALIDO,
            email="maria@email.com",
            telefone="31999999999",
        )
    )
    encontrado = repositorio.buscar_por_id(cliente.id)
    assert encontrado is not None
    assert encontrado.nome == "Maria"


def test_buscar_por_id_inexistente_retorna_none(repositorio):
    assert repositorio.buscar_por_id(9999) is None


def test_buscar_por_documento(repositorio):
    repositorio.salvar(
        Cliente(
            nome="Empresa XYZ",
            tipo_pessoa=TipoPessoa.JURIDICA,
            documento=CNPJ_VALIDO,
            email="contato@xyz.com",
            telefone="31988888888",
        )
    )
    encontrado = repositorio.buscar_por_documento("11222333000181")
    assert encontrado is not None
    assert encontrado.nome == "Empresa XYZ"


def test_documento_duplicado_lanca_erro_de_integridade(repositorio):
    import sqlite3

    repositorio.salvar(
        Cliente(
            nome="Maria",
            tipo_pessoa=TipoPessoa.FISICA,
            documento=CPF_VALIDO,
            email="maria@email.com",
            telefone="31999999999",
        )
    )
    with pytest.raises(sqlite3.IntegrityError):
        repositorio.salvar(
            Cliente(
                nome="Maria Segunda",
                tipo_pessoa=TipoPessoa.FISICA,
                documento=CPF_VALIDO,
                email="outra@email.com",
                telefone="31900000000",
            )
        )


def test_listar_ativos_exclui_inativos(repositorio):
    cliente_ativo = repositorio.salvar(
        Cliente(
            nome="Ativo",
            tipo_pessoa=TipoPessoa.FISICA,
            documento=CPF_VALIDO,
            email="ativo@email.com",
            telefone="31900000000",
        )
    )
    cliente_inativo = repositorio.salvar(
        Cliente(
            nome="Inativo",
            tipo_pessoa=TipoPessoa.JURIDICA,
            documento=CNPJ_VALIDO,
            email="inativo@email.com",
            telefone="31900000000",
        )
    )
    cliente_inativo.inativar()
    repositorio.atualizar(cliente_inativo)

    ativos = repositorio.listar_ativos()
    assert len(ativos) == 1
    assert ativos[0].nome == "Ativo"

    todos = repositorio.listar_todos()
    assert len(todos) == 2


def test_atualizar_persiste_mudancas(repositorio):
    cliente = repositorio.salvar(
        Cliente(
            nome="Maria",
            tipo_pessoa=TipoPessoa.FISICA,
            documento=CPF_VALIDO,
            email="maria@email.com",
            telefone="31999999999",
        )
    )
    cliente.associar_tabela_preco(7)
    repositorio.atualizar(cliente)

    recarregado = repositorio.buscar_por_id(cliente.id)
    assert recarregado.tabela_preco_id == 7