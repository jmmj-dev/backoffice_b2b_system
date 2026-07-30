"""Implementação SQLite do contrato ClienteRepositorio."""
import sqlite3
from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.cliente import Cliente, TipoPessoa
from src.repositorios.contratos.cliente_repositorio import ClienteRepositorio


class ClienteRepositorioSQLite(ClienteRepositorio):
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def salvar(self, cliente: Cliente) -> Cliente:
        cursor = self._conexao.execute(
            """
            INSERT INTO clientes
                (nome, tipo_pessoa, documento, email, telefone, tabela_preco_id, ativo, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cliente.nome,
                cliente.tipo_pessoa.value,
                cliente.documento,
                cliente.email,
                cliente.telefone,
                cliente.tabela_preco_id,
                int(cliente.ativo),
                cliente.data_cadastro.isoformat(),
            ),
        )
        self._conexao.commit()
        cliente.id = cursor.lastrowid
        return cliente

    def buscar_por_id(self, id: int) -> Optional[Cliente]:
        linha = self._conexao.execute("SELECT * FROM clientes WHERE id = ?", (id,)).fetchone()
        return self._linha_para_cliente(linha) if linha else None

    def buscar_por_documento(self, documento: str) -> Optional[Cliente]:
        linha = self._conexao.execute(
            "SELECT * FROM clientes WHERE documento = ?", (documento,)
        ).fetchone()
        return self._linha_para_cliente(linha) if linha else None

    def listar_ativos(self) -> List[Cliente]:
        linhas = self._conexao.execute("SELECT * FROM clientes WHERE ativo = 1").fetchall()
        return [self._linha_para_cliente(linha) for linha in linhas]

    def listar_todos(self) -> List[Cliente]:
        linhas = self._conexao.execute("SELECT * FROM clientes").fetchall()
        return [self._linha_para_cliente(linha) for linha in linhas]

    def atualizar(self, cliente: Cliente) -> Cliente:
        self._conexao.execute(
            """
            UPDATE clientes
            SET nome = ?, tipo_pessoa = ?, documento = ?, email = ?, telefone = ?,
                tabela_preco_id = ?, ativo = ?
            WHERE id = ?
            """,
            (
                cliente.nome,
                cliente.tipo_pessoa.value,
                cliente.documento,
                cliente.email,
                cliente.telefone,
                cliente.tabela_preco_id,
                int(cliente.ativo),
                cliente.id,
            ),
        )
        self._conexao.commit()
        return cliente

    def _linha_para_cliente(self, linha: sqlite3.Row) -> Cliente:
        """Converte uma linha crua do banco de volta para um objeto Cliente."""
        cliente = Cliente(
            nome=linha["nome"],
            tipo_pessoa=TipoPessoa(linha["tipo_pessoa"]),
            documento=linha["documento"],
            email=linha["email"],
            telefone=linha["telefone"],
            tabela_preco_id=linha["tabela_preco_id"],
        )
        cliente.id = linha["id"]
        cliente.ativo = bool(linha["ativo"])
        cliente.data_cadastro = datetime.fromisoformat(linha["data_cadastro"])
        return cliente