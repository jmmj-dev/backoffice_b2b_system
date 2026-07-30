"""Implementação fake em memória do ProdutoRepositorio, usada apenas em testes de serviço."""
import copy
from typing import List, Optional

from src.dominio.entidades.produto import Produto
from src.repositorios.contratos.produto_repositorio import ProdutoRepositorio


class ProdutoRepositorioFake(ProdutoRepositorio):
    def __init__(self) -> None:
        self._produtos: List[Produto] = []
        self._proximo_id = 1

    def salvar(self, produto: Produto) -> Produto:
        produto.id = self._proximo_id
        self._proximo_id += 1
        self._produtos.append(copy.deepcopy(produto))
        return copy.deepcopy(produto)

    def buscar_por_id(self, id: int) -> Optional[Produto]:
        produto = next((p for p in self._produtos if p.id == id), None)
        return copy.deepcopy(produto) if produto else None

    def listar_ativos(self) -> List[Produto]:
        return [copy.deepcopy(p) for p in self._produtos if p.ativo]

    def listar_todos(self) -> List[Produto]:
        return [copy.deepcopy(p) for p in self._produtos]

    def atualizar(self, produto: Produto) -> Produto:
        for i, p in enumerate(self._produtos):
            if p.id == produto.id:
                self._produtos[i] = copy.deepcopy(produto)
                return copy.deepcopy(produto)
        raise ValueError(f"Produto com id {produto.id} não encontrado para atualização.")