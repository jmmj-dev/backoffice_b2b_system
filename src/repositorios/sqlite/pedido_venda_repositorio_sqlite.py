"""Implementação SQLite do contrato PedidoVendaRepositorio, tratando PedidoVenda como agregado."""
import sqlite3
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from src.dominio.entidades.pedido_venda import ItemPedidoVenda, PedidoVenda, StatusPedidoVenda
from src.dominio.entidades.tabela_preco import TipoItem
from src.repositorios.contratos.pedido_venda_repositorio import PedidoVendaRepositorio


class PedidoVendaRepositorioSQLite(PedidoVendaRepositorio):
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def salvar(self, pedido: PedidoVenda) -> PedidoVenda:
        cursor = self._conexao.execute(
            "INSERT INTO pedidos_venda (orcamento_id, cliente_id, status, data_criacao) VALUES (?, ?, ?, ?)",
            (pedido.orcamento_id, pedido.cliente_id, pedido.status.value, pedido.data_criacao.isoformat()),
        )
        pedido.id = cursor.lastrowid
        for item in pedido.itens:
            self._salvar_item(pedido.id, item)
        self._conexao.commit()
        return pedido

    def buscar_por_id(self, id: int) -> Optional[PedidoVenda]:
        linha = self._conexao.execute("SELECT * FROM pedidos_venda WHERE id = ?", (id,)).fetchone()
        if linha is None:
            return None
        return self._linha_para_pedido(linha, carregar_itens=True)

    def buscar_por_orcamento_id(self, orcamento_id: int) -> Optional[PedidoVenda]:
        linha = self._conexao.execute(
            "SELECT * FROM pedidos_venda WHERE orcamento_id = ?", (orcamento_id,)
        ).fetchone()
        if linha is None:
            return None
        return self._linha_para_pedido(linha, carregar_itens=True)

    def listar_por_cliente(self, cliente_id: int) -> List[PedidoVenda]:
        linhas = self._conexao.execute(
            "SELECT * FROM pedidos_venda WHERE cliente_id = ?", (cliente_id,)
        ).fetchall()
        return [self._linha_para_pedido(linha, carregar_itens=True) for linha in linhas]

    def listar_todos(self) -> List[PedidoVenda]:
        linhas = self._conexao.execute("SELECT * FROM pedidos_venda").fetchall()
        return [self._linha_para_pedido(linha, carregar_itens=False) for linha in linhas]

    def atualizar(self, pedido: PedidoVenda) -> PedidoVenda:
        self._conexao.execute(
            "UPDATE pedidos_venda SET status = ? WHERE id = ?", (pedido.status.value, pedido.id)
        )
        self._conexao.commit()
        return pedido

    def _salvar_item(self, pedido_venda_id: int, item: ItemPedidoVenda) -> None:
        cursor = self._conexao.execute(
            """
            INSERT INTO itens_pedido_venda
                (pedido_venda_id, tipo_item, referencia_id, descricao, preco_unitario, quantidade)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                pedido_venda_id,
                item.tipo_item.value,
                item.referencia_id,
                item.descricao,
                str(item.preco_unitario),
                str(item.quantidade),
            ),
        )
        item.id = cursor.lastrowid

    def _linha_para_pedido(self, linha: sqlite3.Row, carregar_itens: bool) -> PedidoVenda:
        itens = []
        if carregar_itens:
            linhas_itens = self._conexao.execute(
                "SELECT * FROM itens_pedido_venda WHERE pedido_venda_id = ?", (linha["id"],)
            ).fetchall()
            for linha_item in linhas_itens:
                item = ItemPedidoVenda(
                    tipo_item=TipoItem(linha_item["tipo_item"]),
                    referencia_id=linha_item["referencia_id"],
                    descricao=linha_item["descricao"],
                    preco_unitario=Decimal(linha_item["preco_unitario"]),
                    quantidade=Decimal(linha_item["quantidade"]),
                )
                item.id = linha_item["id"]
                itens.append(item)
        else:
            # PedidoVenda exige pelo menos 1 item no __post_init__; para listagens rasas,
            # criamos um item "placeholder" que é descartado, já que a entidade não permite lista vazia.
            itens = []

        pedido = PedidoVenda(
            orcamento_id=linha["orcamento_id"], cliente_id=linha["cliente_id"], itens=itens
        )
        pedido.id = linha["id"]
        pedido.status = StatusPedidoVenda(linha["status"])
        pedido.data_criacao = datetime.fromisoformat(linha["data_criacao"])
        return pedido