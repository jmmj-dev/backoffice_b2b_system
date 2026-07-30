"""Implementação fake em memória do ServicoRepositorio, usada apenas em testes de serviço."""
import copy
from typing import List, Optional

from src.dominio.entidades.servico import Servico
from src.repositorios.contratos.servico_repositorio import ServicoRepositorio


class ServicoRepositorioFake(ServicoRepositorio):
    def __init__(self) -> None:
        self._servicos: List[Servico] = []
        self._proximo_id = 1

    def salvar(self, servico: Servico) -> Servico:
        servico.id = self._proximo_id
        self._proximo_id += 1
        self._servicos.append(copy.deepcopy(servico))
        return copy.deepcopy(servico)

    def buscar_por_id(self, id: int) -> Optional[Servico]:
        servico = next((s for s in self._servicos if s.id == id), None)
        return copy.deepcopy(servico) if servico else None

    def listar_ativos(self) -> List[Servico]:
        return [copy.deepcopy(s) for s in self._servicos if s.ativo]

    def listar_todos(self) -> List[Servico]:
        return [copy.deepcopy(s) for s in self._servicos]

    def atualizar(self, servico: Servico) -> Servico:
        for i, s in enumerate(self._servicos):
            if s.id == servico.id:
                self._servicos[i] = copy.deepcopy(servico)
                return copy.deepcopy(servico)
        raise ValueError(f"Serviço com id {servico.id} não encontrado para atualização.")