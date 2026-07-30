"""ServicoServico: orquestra as regras de negócio de cadastro e gestão de serviços prestados."""
from typing import List

from src.dominio.entidades.servico import Servico
from src.repositorios.contratos.servico_repositorio import ServicoRepositorio


class ServicoServico:
    def __init__(self, servico_repositorio: ServicoRepositorio) -> None:
        self._repositorio = servico_repositorio

    def criar_servico(self, servico: Servico) -> Servico:
        return self._repositorio.salvar(servico)

    def atualizar_servico(self, servico: Servico) -> Servico:
        if servico.id is None:
            raise ValueError("Não é possível atualizar um serviço sem id.")
        self._buscar_ou_lancar_erro(servico.id)
        return self._repositorio.atualizar(servico)

    def inativar_servico(self, id: int) -> Servico:
        servico = self._buscar_ou_lancar_erro(id)
        servico.inativar()
        return self._repositorio.atualizar(servico)

    def reativar_servico(self, id: int) -> Servico:
        servico = self._buscar_ou_lancar_erro(id)
        servico.reativar()
        return self._repositorio.atualizar(servico)

    def buscar_por_id(self, id: int) -> Servico:
        return self._buscar_ou_lancar_erro(id)

    def listar_servicos_ativos(self) -> List[Servico]:
        return self._repositorio.listar_ativos()

    def listar_todos_os_servicos(self) -> List[Servico]:
        return self._repositorio.listar_todos()

    def _buscar_ou_lancar_erro(self, id: int) -> Servico:
        servico = self._repositorio.buscar_por_id(id)
        if servico is None:
            raise ValueError(f"Serviço com id {id} não encontrado.")
        return servico