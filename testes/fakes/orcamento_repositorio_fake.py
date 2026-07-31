"""Implementação fake em memória do OrcamentoRepositorio, usada apenas em testes de serviço."""
import copy
from typing import List, Optional

from src.dominio.entidades.orcamento import Orcamento
from src.repositorios.contratos.orcamento_repositorio import OrcamentoRepositorio


class OrcamentoRepositorioFake(OrcamentoRepositorio):
    def __init__(self) -> None:
        self._orcamentos: List[Orcamento] = []
        self._proximo_id = 1
        self._proximo_id_item = 1
        self._proximo_id_registro = 1

    def salvar(self, orcamento: Orcamento) -> Orcamento:
        orcamento.id = self._proximo_id
        self._proximo_id += 1
        self._atribuir_ids_pendentes(orcamento)
        self._orcamentos.append(copy.deepcopy(orcamento))
        return copy.deepcopy(orcamento)

    def buscar_por_id(self, id: int) -> Optional[Orcamento]:
        orcamento = next((o for o in self._orcamentos if o.id == id), None)
        return copy.deepcopy(orcamento) if orcamento else None

    def listar_por_cliente(self, cliente_id: int) -> List[Orcamento]:
        return [copy.deepcopy(o) for o in self._orcamentos if o.cliente_id == cliente_id]

    def listar_todos(self) -> List[Orcamento]:
        return [copy.deepcopy(o) for o in self._orcamentos]

    def atualizar(self, orcamento: Orcamento) -> Orcamento:
        self._atribuir_ids_pendentes(orcamento)
        for i, o in enumerate(self._orcamentos):
            if o.id == orcamento.id:
                self._orcamentos[i] = copy.deepcopy(orcamento)
                return copy.deepcopy(orcamento)
        raise ValueError(f"Orçamento com id {orcamento.id} não encontrado para atualização.")

    def _atribuir_ids_pendentes(self, orcamento: Orcamento) -> None:
        for item in orcamento.itens:
            if item.id is None:
                item.id = self._proximo_id_item
                self._proximo_id_item += 1
        for registro in orcamento.historico:
            if registro.id is None:
                registro.id = self._proximo_id_registro
                self._proximo_id_registro += 1