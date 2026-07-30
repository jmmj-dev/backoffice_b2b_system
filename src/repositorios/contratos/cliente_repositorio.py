"""Contrato (interface abstrata) para persistência de Cliente."""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.dominio.entidades.cliente import Cliente


class ClienteRepositorio(ABC):
    @abstractmethod
    def salvar(self, cliente: Cliente) -> Cliente:
        """Persiste um novo cliente e retorna ele com o id preenchido."""

    @abstractmethod
    def buscar_por_id(self, id: int) -> Optional[Cliente]:
        """Busca um cliente pelo id. Retorna None se não encontrado."""

    @abstractmethod
    def buscar_por_documento(self, documento: str) -> Optional[Cliente]:
        """Busca um cliente pelo CPF/CNPJ (já limpo, sem pontuação)."""

    @abstractmethod
    def listar_ativos(self) -> List[Cliente]:
        """Lista apenas clientes ativos."""

    @abstractmethod
    def listar_todos(self) -> List[Cliente]:
        """Lista todos os clientes, ativos e inativos."""

    @abstractmethod
    def atualizar(self, cliente: Cliente) -> Cliente:
        """Atualiza os dados de um cliente já existente (identificado pelo id)."""