"""Implementação SQLite do contrato ServicoRepositorio."""
import sqlite3
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from src.dominio.entidades.servico import Servico
from src.repositorios.contratos.servico_repositorio import ServicoRepositorio


class ServicoRepositorioSQLite(ServicoRepositorio):
    def __init__(self, conexao: sqlite3.Connection) -> None:
        self._conexao = conexao

    def salvar(self, servico: Servico) -> Servico:
        cursor = self._conexao.execute(
            """
            INSERT INTO servicos (nome, valor_hora, horas_estimadas, descricao, ativo, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                servico.nome,
                str(servico.valor_hora),
                str(servico.horas_estimadas),
                servico.descricao,
                int(servico.ativo),
                servico.data_cadastro.isoformat(),
            ),
        )
        self._conexao.commit()
        servico.id = cursor.lastrowid
        return servico

    def buscar_por_id(self, id: int) -> Optional[Servico]:
        linha = self._conexao.execute("SELECT * FROM servicos WHERE id = ?", (id,)).fetchone()
        return self._linha_para_servico(linha) if linha else None

    def listar_ativos(self) -> List[Servico]:
        linhas = self._conexao.execute("SELECT * FROM servicos WHERE ativo = 1").fetchall()
        return [self._linha_para_servico(linha) for linha in linhas]

    def listar_todos(self) -> List[Servico]:
        linhas = self._conexao.execute("SELECT * FROM servicos").fetchall()
        return [self._linha_para_servico(linha) for linha in linhas]

    def atualizar(self, servico: Servico) -> Servico:
        self._conexao.execute(
            """
            UPDATE servicos
            SET nome = ?, valor_hora = ?, horas_estimadas = ?, descricao = ?, ativo = ?
            WHERE id = ?
            """,
            (
                servico.nome,
                str(servico.valor_hora),
                str(servico.horas_estimadas),
                servico.descricao,
                int(servico.ativo),
                servico.id,
            ),
        )
        self._conexao.commit()
        return servico

    def _linha_para_servico(self, linha: sqlite3.Row) -> Servico:
        servico = Servico(
            nome=linha["nome"],
            valor_hora=Decimal(linha["valor_hora"]),
            horas_estimadas=Decimal(linha["horas_estimadas"]),
            descricao=linha["descricao"] or "",
        )
        servico.id = linha["id"]
        servico.ativo = bool(linha["ativo"])
        servico.data_cadastro = datetime.fromisoformat(linha["data_cadastro"])
        return servico