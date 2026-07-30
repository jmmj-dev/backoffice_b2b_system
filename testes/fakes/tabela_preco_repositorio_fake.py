"""Implementação fake em memória do TabelaPrecoRepositorio, usada apenas em testes de serviço."""
import copy
from typing import List, Optional

from src.dominio.entidades.tabela_preco import TabelaPreco
from src.repositorios.contratos.tabela_preco_repositorio import TabelaPrecoRepositorio


class TabelaPrecoRepositorioFake(TabelaPrecoRepositorio):
    def __init__(self) -> None:
        self._tabelas: List[TabelaPreco] = []
        self._proximo_id = 1
        self._proximo_id_item = 1

    def salvar(self, tabela: TabelaPreco) -> TabelaPreco:
        tabela.id = self._proximo_id
        self._proximo_id += 1
        for item in tabela.itens:
            item.id = self._proximo_id_item
            self._proximo_id_item += 1
        self._tabelas.append(copy.deepcopy(tabela))
        return copy.deepcopy(tabela)

    def buscar_por_id(self, id: int) -> Optional[TabelaPreco]:
        tabela = next((t for t in self._tabelas if t.id == id), None)
        return copy.deepcopy(tabela) if tabela else None

    def listar_ativas(self) -> List[TabelaPreco]:
        return [copy.deepcopy(t) for t in self._tabelas if t.ativa]

    def listar_todas(self) -> List[TabelaPreco]:
        return [copy.deepcopy(t) for t in self._tabelas]

    def atualizar(self, tabela: TabelaPreco) -> TabelaPreco:
        for item in tabela.itens:
            if item.id is None:
                item.id = self._proximo_id_item
                self._proximo_id_item += 1
        for i, t in enumerate(self._tabelas):
            if t.id == tabela.id:
                self._tabelas[i] = copy.deepcopy(tabela)
                return copy.deepcopy(tabela)
        raise ValueError(f"Tabela de preço com id {tabela.id} não encontrada para atualização.")