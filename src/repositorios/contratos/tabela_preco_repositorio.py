"""Contrato (interface abstrata) para persistência de TabelaPreco (agregado, com seus itens)."""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.dominio.entidades.tabela_preco import TabelaPreco


class TabelaPrecoRepositorio(ABC):
    @abstractmethod
    def salvar(self, tabela: TabelaPreco) -> TabelaPreco:
        """Persiste uma nova tabela de preço e todos os itens que ela já tiver."""

    @abstractmethod
    def buscar_por_id(self, id: int) -> Optional[TabelaPreco]:
        """Busca uma tabela de preço, já com seus itens carregados. Retorna None se não encontrada."""

    @abstractmethod
    def listar_ativas(self) -> List[TabelaPreco]:
        """Lista apenas tabelas de preço ativas (sem carregar itens, para listagens rápidas)."""

    @abstractmethod
    def listar_todas(self) -> List[TabelaPreco]:
        """Lista todas as tabelas de preço, ativas e inativas."""

    @abstractmethod
    def atualizar(self, tabela: TabelaPreco) -> TabelaPreco:
        """Atualiza a tabela e sincroniza (insere/atualiza) todos os itens da lista em memória."""