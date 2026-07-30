"""Implementação SQLite do contrato ProdutoRepositorio."""
import sqlite3
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from src.dominio.entidades.produto import Produto, UnidadeMedida
from src.repositorios.contratos.produto_repositorio import ProdutoRepositorio


class ProdutoRepositorioSQLite(ProdutoRepositorio):
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def salvar(self, produto: Produto) -> Produto:
        cursor = self._conexao.execute(
            """
            INSERT INTO produtos (nome, unidade_medida, preco_unitario, descricao, ativo, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                produto.nome,
                produto.unidade_medida.value,
                str(produto.preco_unitario),
                produto.descricao,
                int(produto.ativo),
                produto.data_cadastro.isoformat(),
            ),
        )
        self._conexao.commit()
        produto.id = cursor.lastrowid
        return produto

    def buscar_por_id(self, id: int) -> Optional[Produto]:
        linha = self._conexao.execute("SELECT * FROM produtos WHERE id = ?", (id,)).fetchone()
        return self._linha_para_produto(linha) if linha else None

    def listar_ativos(self) -> List[Produto]:
        linhas = self._conexao.execute("SELECT * FROM produtos WHERE ativo = 1").fetchall()
        return [self._linha_para_produto(linha) for linha in linhas]

    def listar_todos(self) -> List[Produto]:
        linhas = self._conexao.execute("SELECT * FROM produtos").fetchall()
        return [self._linha_para_produto(linha) for linha in linhas]

    def atualizar(self, produto: Produto) -> Produto:
        self._conexao.execute(
            """
            UPDATE produtos
            SET nome = ?, unidade_medida = ?, preco_unitario = ?, descricao = ?, ativo = ?
            WHERE id = ?
            """,
            (
                produto.nome,
                produto.unidade_medida.value,
                str(produto.preco_unitario),
                produto.descricao,
                int(produto.ativo),
                produto.id,
            ),
        )
        self._conexao.commit()
        return produto

    def _linha_para_produto(self, linha: sqlite3.Row) -> Produto:
        produto = Produto(
            nome=linha["nome"],
            unidade_medida=UnidadeMedida(linha["unidade_medida"]),
            preco_unitario=Decimal(linha["preco_unitario"]),
            descricao=linha["descricao"] or "",
        )
        produto.id = linha["id"]
        produto.ativo = bool(linha["ativo"])
        produto.data_cadastro = datetime.fromisoformat(linha["data_cadastro"])
        return produto