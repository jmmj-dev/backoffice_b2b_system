"""Implementação SQLite do contrato TabelaPrecoRepositorio, tratando TabelaPreco como agregado."""
import sqlite3
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from src.dominio.entidades.tabela_preco import ItemTabelaPreco, TabelaPreco, TipoItem
from src.repositorios.contratos.tabela_preco_repositorio import TabelaPrecoRepositorio


class TabelaPrecoRepositorioSQLite(TabelaPrecoRepositorio):
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def salvar(self, tabela: TabelaPreco) -> TabelaPreco:
        cursor = self._conexao.execute(
            "INSERT INTO tabelas_preco (nome, descricao, ativa, data_cadastro) VALUES (?, ?, ?, ?)",
            (tabela.nome, tabela.descricao, int(tabela.ativa), tabela.data_cadastro.isoformat()),
        )
        tabela.id = cursor.lastrowid
        for item in tabela.itens:
            self._salvar_item(tabela.id, item)
        self._conexao.commit()
        return tabela

    def buscar_por_id(self, id: int) -> Optional[TabelaPreco]:
        linha = self._conexao.execute("SELECT * FROM tabelas_preco WHERE id = ?", (id,)).fetchone()
        if linha is None:
            return None
        return self._linha_para_tabela(linha, carregar_itens=True)

    def listar_ativas(self) -> List[TabelaPreco]:
        linhas = self._conexao.execute("SELECT * FROM tabelas_preco WHERE ativa = 1").fetchall()
        return [self._linha_para_tabela(linha, carregar_itens=False) for linha in linhas]

    def listar_todas(self) -> List[TabelaPreco]:
        linhas = self._conexao.execute("SELECT * FROM tabelas_preco").fetchall()
        return [self._linha_para_tabela(linha, carregar_itens=False) for linha in linhas]

    def atualizar(self, tabela: TabelaPreco) -> TabelaPreco:
        self._conexao.execute(
            "UPDATE tabelas_preco SET nome = ?, descricao = ?, ativa = ? WHERE id = ?",
            (tabela.nome, tabela.descricao, int(tabela.ativa), tabela.id),
        )
        for item in tabela.itens:
            self._salvar_item(tabela.id, item)
        self._conexao.commit()
        return tabela

    def _salvar_item(self, tabela_preco_id: int, item: ItemTabelaPreco) -> None:
        """Insere o item se ele ainda não tem id, ou atualiza se já existir. (Upsert simples)"""
        if item.id is None:
            cursor = self._conexao.execute(
                """
                INSERT INTO itens_tabela_preco (tabela_preco_id, tipo_item, referencia_id, preco, ativo)
                VALUES (?, ?, ?, ?, ?)
                """,
                (tabela_preco_id, item.tipo_item.value, item.referencia_id, str(item.preco), int(item.ativo)),
            )
            item.id = cursor.lastrowid
        else:
            self._conexao.execute(
                "UPDATE itens_tabela_preco SET preco = ?, ativo = ? WHERE id = ?",
                (str(item.preco), int(item.ativo), item.id),
            )

    def _linha_para_tabela(self, linha: sqlite3.Row, carregar_itens: bool) -> TabelaPreco:
        tabela = TabelaPreco(nome=linha["nome"], descricao=linha["descricao"] or "")
        tabela.id = linha["id"]
        tabela.ativa = bool(linha["ativa"])
        tabela.data_cadastro = datetime.fromisoformat(linha["data_cadastro"])

        if carregar_itens:
            linhas_itens = self._conexao.execute(
                "SELECT * FROM itens_tabela_preco WHERE tabela_preco_id = ?", (tabela.id,)
            ).fetchall()
            for linha_item in linhas_itens:
                item = ItemTabelaPreco(
                    tipo_item=TipoItem(linha_item["tipo_item"]),
                    referencia_id=linha_item["referencia_id"],
                    preco=Decimal(linha_item["preco"]),
                )
                item.id = linha_item["id"]
                item.ativo = bool(linha_item["ativo"])
                tabela.itens.append(item)

        return tabela