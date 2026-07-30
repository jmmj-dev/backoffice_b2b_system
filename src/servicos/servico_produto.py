"""ServicoProduto: orquestra as regras de negócio de cadastro e gestão de produtos."""
from typing import List

from src.dominio.entidades.produto import Produto
from src.repositorios.contratos.produto_repositorio import ProdutoRepositorio


class ServicoProduto:
    def __init__(self, produto_repositorio: ProdutoRepositorio) -> None:
        self._repositorio = produto_repositorio

    def criar_produto(self, produto: Produto) -> Produto:
        return self._repositorio.salvar(produto)

    def atualizar_produto(self, produto: Produto) -> Produto:
        if produto.id is None:
            raise ValueError("Não é possível atualizar um produto sem id.")
        self._buscar_ou_lancar_erro(produto.id)
        return self._repositorio.atualizar(produto)

    def inativar_produto(self, id: int) -> Produto:
        produto = self._buscar_ou_lancar_erro(id)
        produto.inativar()
        return self._repositorio.atualizar(produto)

    def reativar_produto(self, id: int) -> Produto:
        produto = self._buscar_ou_lancar_erro(id)
        produto.reativar()
        return self._repositorio.atualizar(produto)

    def buscar_por_id(self, id: int) -> Produto:
        return self._buscar_ou_lancar_erro(id)

    def listar_produtos_ativos(self) -> List[Produto]:
        return self._repositorio.listar_ativos()

    def listar_todos_os_produtos(self) -> List[Produto]:
        return self._repositorio.listar_todos()

    def _buscar_ou_lancar_erro(self, id: int) -> Produto:
        produto = self._repositorio.buscar_por_id(id)
        if produto is None:
            raise ValueError(f"Produto com id {id} não encontrado.")
        return produto