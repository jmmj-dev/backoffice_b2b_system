"""Contrato (interface abstrata) para persistência de Servico."""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.dominio.entidades.servico import Servico


class ServicoRepositorio(ABC):
    @abstractmethod
    def salvar(self, servico: Servico) -> Servico:
        """Persiste um novo serviço e retorna ele com o id preenchido."""

    @abstractmethod
    def buscar_por_id(self, id: int) -> Optional[Servico]:
        """Busca um serviço pelo id. Retorna None se não encontrado."""

    @abstractmethod
    def listar_ativos(self) -> List[Servico]:
        """Lista apenas serviços ativos."""

    @abstractmethod
    def listar_todos(self) -> List[Servico]:
        """Lista todos os serviços, ativos e inativos."""

    @abstractmethod
    def atualizar(self, servico: Servico) -> Servico:
        """Atualiza os dados de um serviço já existente (identificado pelo id)."""