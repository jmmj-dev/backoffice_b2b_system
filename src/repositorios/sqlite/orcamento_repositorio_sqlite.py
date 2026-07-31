"""Implementação SQLite do contrato OrcamentoRepositorio, tratando Orcamento como agregado
(itens + histórico de negociação)."""
import sqlite3
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from src.dominio.entidades.orcamento import (
    ItemOrcamento,
    Orcamento,
    RegistroHistorico,
    StatusOrcamento,
    TipoRegistroHistorico,
)
from src.dominio.entidades.tabela_preco import TipoItem
from src.repositorios.contratos.orcamento_repositorio import OrcamentoRepositorio


class OrcamentoRepositorioSQLite(OrcamentoRepositorio):
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def salvar(self, orcamento: Orcamento) -> Orcamento:
        cursor = self._conexao.execute(
            """
            INSERT INTO orcamentos
                (cliente_id, tabela_preco_id, data_validade, status, desconto_percentual, data_criacao)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                orcamento.cliente_id,
                orcamento.tabela_preco_id,
                orcamento.data_validade.isoformat(),
                orcamento.status.value,
                str(orcamento.desconto_percentual),
                orcamento.data_criacao.isoformat(),
            ),
        )
        orcamento.id = cursor.lastrowid
        for item in orcamento.itens:
            self._salvar_item(orcamento.id, item)
        for registro in orcamento.historico:
            self._salvar_registro_historico(orcamento.id, registro)
        self._conexao.commit()
        return orcamento

    def buscar_por_id(self, id: int) -> Optional[Orcamento]:
        linha = self._conexao.execute("SELECT * FROM orcamentos WHERE id = ?", (id,)).fetchone()
        if linha is None:
            return None
        return self._linha_para_orcamento(linha, carregar_detalhes=True)

    def listar_por_cliente(self, cliente_id: int) -> List[Orcamento]:
        linhas = self._conexao.execute(
            "SELECT * FROM orcamentos WHERE cliente_id = ?", (cliente_id,)
        ).fetchall()
        return [self._linha_para_orcamento(linha, carregar_detalhes=True) for linha in linhas]

    def listar_todos(self) -> List[Orcamento]:
        linhas = self._conexao.execute("SELECT * FROM orcamentos").fetchall()
        return [self._linha_para_orcamento(linha, carregar_detalhes=False) for linha in linhas]

    def atualizar(self, orcamento: Orcamento) -> Orcamento:
        self._conexao.execute(
            """
            UPDATE orcamentos
            SET data_validade = ?, status = ?, desconto_percentual = ?
            WHERE id = ?
            """,
            (
                orcamento.data_validade.isoformat(),
                orcamento.status.value,
                str(orcamento.desconto_percentual),
                orcamento.id,
            ),
        )
        for item in orcamento.itens:
            self._salvar_item(orcamento.id, item)
        for registro in orcamento.historico:
            self._salvar_registro_historico(orcamento.id, registro)
        self._conexao.commit()
        return orcamento

    def _salvar_item(self, orcamento_id: int, item: ItemOrcamento) -> None:
        if item.id is None:
            cursor = self._conexao.execute(
                """
                INSERT INTO itens_orcamento
                    (orcamento_id, tipo_item, referencia_id, descricao, preco_unitario, quantidade, ativo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    orcamento_id,
                    item.tipo_item.value,
                    item.referencia_id,
                    item.descricao,
                    str(item.preco_unitario),
                    str(item.quantidade),
                    int(item.ativo),
                ),
            )
            item.id = cursor.lastrowid
        else:
            self._conexao.execute(
                "UPDATE itens_orcamento SET ativo = ? WHERE id = ?",
                (int(item.ativo), item.id),
            )

    def _salvar_registro_historico(self, orcamento_id: int, registro: RegistroHistorico) -> None:
        """Insere um registro de histórico novo. Registros de histórico nunca são atualizados
        ou apagados depois de criados — são um log de auditoria imutável."""
        if registro.id is None:
            cursor = self._conexao.execute(
                "INSERT INTO historico_orcamento (orcamento_id, tipo, descricao, data_hora) VALUES (?, ?, ?, ?)",
                (orcamento_id, registro.tipo.value, registro.descricao, registro.data_hora.isoformat()),
            )
            registro.id = cursor.lastrowid

    def _linha_para_orcamento(self, linha: sqlite3.Row, carregar_detalhes: bool) -> Orcamento:
        orcamento = Orcamento(
            cliente_id=linha["cliente_id"],
            tabela_preco_id=linha["tabela_preco_id"],
            data_validade=date.fromisoformat(linha["data_validade"]),
        )
        orcamento.id = linha["id"]
        orcamento.status = StatusOrcamento(linha["status"])
        orcamento.desconto_percentual = Decimal(linha["desconto_percentual"])
        orcamento.data_criacao = datetime.fromisoformat(linha["data_criacao"])

        if carregar_detalhes:
            linhas_itens = self._conexao.execute(
                "SELECT * FROM itens_orcamento WHERE orcamento_id = ?", (orcamento.id,)
            ).fetchall()
            for linha_item in linhas_itens:
                item = ItemOrcamento(
                    tipo_item=TipoItem(linha_item["tipo_item"]),
                    referencia_id=linha_item["referencia_id"],
                    descricao=linha_item["descricao"],
                    preco_unitario=Decimal(linha_item["preco_unitario"]),
                    quantidade=Decimal(linha_item["quantidade"]),
                )
                item.id = linha_item["id"]
                item.ativo = bool(linha_item["ativo"])
                orcamento.itens.append(item)

            linhas_historico = self._conexao.execute(
                "SELECT * FROM historico_orcamento WHERE orcamento_id = ? ORDER BY data_hora",
                (orcamento.id,),
            ).fetchall()
            for linha_registro in linhas_historico:
                registro = RegistroHistorico(
                    tipo=TipoRegistroHistorico(linha_registro["tipo"]),
                    descricao=linha_registro["descricao"],
                )
                registro.id = linha_registro["id"]
                registro.data_hora = datetime.fromisoformat(linha_registro["data_hora"])
                orcamento.historico.append(registro)

        return orcamento