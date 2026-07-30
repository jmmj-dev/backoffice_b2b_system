"""Define e cria as tabelas do banco de dados."""
import sqlite3


def criar_tabelas(conexao: sqlite3.Connection) -> None:
    """Cria todas as tabelas do sistema, se ainda não existirem."""
    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo_pessoa TEXT NOT NULL,
            documento TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            telefone TEXT NOT NULL,
            tabela_preco_id INTEGER,
            ativo INTEGER NOT NULL DEFAULT 1,
            data_cadastro TEXT NOT NULL
        )
        """
    )
    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            unidade_medida TEXT NOT NULL,
            preco_unitario TEXT NOT NULL,
            descricao TEXT,
            ativo INTEGER NOT NULL DEFAULT 1,
            data_cadastro TEXT NOT NULL
        )
        """
    )
    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            valor_hora TEXT NOT NULL,
            horas_estimadas TEXT NOT NULL,
            descricao TEXT,
            ativo INTEGER NOT NULL DEFAULT 1,
            data_cadastro TEXT NOT NULL
        )
        """
    )
    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS tabelas_preco (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            ativa INTEGER NOT NULL DEFAULT 1,
            data_cadastro TEXT NOT NULL
        )
        """
    )
    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS itens_tabela_preco (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tabela_preco_id INTEGER NOT NULL,
            tipo_item TEXT NOT NULL,
            referencia_id INTEGER NOT NULL,
            preco TEXT NOT NULL,
            ativo INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (tabela_preco_id) REFERENCES tabelas_preco (id)
        )
        """
    )
    conexao.commit()