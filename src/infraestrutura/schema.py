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
    conexao.commit()