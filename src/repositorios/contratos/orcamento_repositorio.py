"""Contrato (interface abstrata) para persistência de Orcamento (agregado, com seus itens)."""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.dominio.entidades.orcamento import Orcamento


class OrcamentoRepositorio(ABC):
    @abstractmethod
    def salvar(self, orcamento: Orcamento) -> Orcamento:
        """Persiste um novo orçamento e todos os itens que ele já tiver."""

    @abstractmethod
    def buscar_por_id(self, id: int) -> Optional[Orcamento]:
        """Busca um orçamento, já com seus itens carregados. Retorna None se não encontrado."""

    @abstractmethod
    def listar_por_cliente(self, cliente_id: int) -> List[Orcamento]:
        """Lista todos os orçamentos de um cliente específico (com itens carregados)."""

    @abstractmethod
    def listar_todos(self) -> List[Orcamento]:
        """Lista todos os orçamentos do sistema (sem carregar itens, para listagens rápidas)."""

    @abstractmethod
    def atualizar(self, orcamento: Orcamento) -> Orcamento:
        """Atualiza o orçamento e sincroniza (insere/atualiza) todos os itens da lista em memória."""