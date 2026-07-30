"""Gerencia a conexão com o banco SQLite, isolando por ambiente (dev/teste/prod)."""
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

CAMINHOS_BANCO = {
    "desenvolvimento": "dados/backoffice_dev.db",
    "producao": "dados/backoffice_prod.db",
    "teste": "dados/backoffice_teste.db",
}


def obter_caminho_banco() -> str:
    """Retorna o caminho do arquivo .db correspondente ao ambiente atual (lido do .env)."""
    ambiente = os.getenv("AMBIENTE", "desenvolvimento")
    caminho = CAMINHOS_BANCO.get(ambiente)
    if caminho is None:
        raise ValueError(
            f"Ambiente '{ambiente}' desconhecido. Valores aceitos: {list(CAMINHOS_BANCO.keys())}"
        )
    return caminho


def obter_conexao() -> sqlite3.Connection:
    """Abre (criando se necessário) a conexão com o banco do ambiente atual."""
    caminho = obter_caminho_banco()
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao