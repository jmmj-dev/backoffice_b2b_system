"""Contrato (interface abstrata) para persistência de Produto."""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.dominio.entidades.produto import Produto


class ProdutoRepositorio(ABC):
    @abstractmethod
    def salvar(self, produto: Produto) -> Produto:
        """Persiste um novo produto e retorna ele com o id preenchido."""

    @abstractmethod
    def buscar_por_id(self, id: int) -> Optional[Produto]:
        """Busca um produto pelo id. Retorna None se não encontrado."""

    @abstractmethod
    def listar_ativos(self) -> List[Produto]:
        """Lista apenas produtos ativos."""

    @abstractmethod
    def listar_todos(self) -> List[Produto]:
        """Lista todos os produtos, ativos e inativos."""

    @abstractmethod
    def atualizar(self, produto: Produto) -> Produto:
        """Atualiza os dados de um produto já existente (identificado pelo id)."""