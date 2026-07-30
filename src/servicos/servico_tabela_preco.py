"""ServicoTabelaPreco: orquestra regras de negócio de tabelas de preço, validando
referências a Produto/Serviço antes de aceitar um item."""
from decimal import Decimal
from typing import List

from src.dominio.entidades.tabela_preco import ItemTabelaPreco, TabelaPreco, TipoItem
from src.repositorios.contratos.produto_repositorio import ProdutoRepositorio
from src.repositorios.contratos.servico_repositorio import ServicoRepositorio
from src.repositorios.contratos.tabela_preco_repositorio import TabelaPrecoRepositorio


class ServicoTabelaPreco:
    def __init__(
        self,
        tabela_preco_repositorio: TabelaPrecoRepositorio,
        produto_repositorio: ProdutoRepositorio,
        servico_repositorio: ServicoRepositorio,
    ) -> None:
        self._repositorio = tabela_preco_repositorio
        self._produto_repositorio = produto_repositorio
        self._servico_repositorio = servico_repositorio

    def criar_tabela(self, tabela: TabelaPreco) -> TabelaPreco:
        return self._repositorio.salvar(tabela)

    def adicionar_item(
        self, tabela_id: int, tipo_item: TipoItem, referencia_id: int, preco: Decimal
    ) -> ItemTabelaPreco:
        """Adiciona um item de preço, validando antes que o produto/serviço referenciado existe e está ativo."""
        tabela = self._buscar_tabela_ou_lancar_erro(tabela_id)
        self._validar_referencia_ativa(tipo_item, referencia_id)

        item = tabela.adicionar_item(tipo_item, referencia_id, preco)
        self._repositorio.atualizar(tabela)
        return item

    def atualizar_preco_item(
        self, tabela_id: int, tipo_item: TipoItem, referencia_id: int, novo_preco: Decimal
    ) -> None:
        tabela = self._buscar_tabela_ou_lancar_erro(tabela_id)
        tabela.atualizar_preco_item(tipo_item, referencia_id, novo_preco)
        self._repositorio.atualizar(tabela)

    def remover_item(self, tabela_id: int, tipo_item: TipoItem, referencia_id: int) -> None:
        tabela = self._buscar_tabela_ou_lancar_erro(tabela_id)
        tabela.remover_item(tipo_item, referencia_id)
        self._repositorio.atualizar(tabela)

    def inativar_tabela(self, id: int) -> TabelaPreco:
        tabela = self._buscar_tabela_ou_lancar_erro(id)
        tabela.inativar()
        return self._repositorio.atualizar(tabela)

    def reativar_tabela(self, id: int) -> TabelaPreco:
        tabela = self._buscar_tabela_ou_lancar_erro(id)
        tabela.reativar()
        return self._repositorio.atualizar(tabela)

    def buscar_por_id(self, id: int) -> TabelaPreco:
        return self._buscar_tabela_ou_lancar_erro(id)

    def listar_tabelas_ativas(self) -> List[TabelaPreco]:
        return self._repositorio.listar_ativas()

    def listar_todas_as_tabelas(self) -> List[TabelaPreco]:
        return self._repositorio.listar_todas()

    def _buscar_tabela_ou_lancar_erro(self, id: int) -> TabelaPreco:
        tabela = self._repositorio.buscar_por_id(id)
        if tabela is None:
            raise ValueError(f"Tabela de preço com id {id} não encontrada.")
        return tabela

    def _validar_referencia_ativa(self, tipo_item: TipoItem, referencia_id: int) -> None:
        """Garante que o produto ou serviço referenciado existe e está ativo antes de precificá-lo."""
        if tipo_item == TipoItem.PRODUTO:
            produto = self._produto_repositorio.buscar_por_id(referencia_id)
            if produto is None:
                raise ValueError(f"Produto com id {referencia_id} não encontrado.")
            if not produto.ativo:
                raise ValueError(f"Produto '{produto.nome}' está inativo e não pode receber preço.")
        elif tipo_item == TipoItem.SERVICO:
            servico = self._servico_repositorio.buscar_por_id(referencia_id)
            if servico is None:
                raise ValueError(f"Serviço com id {referencia_id} não encontrado.")
            if not servico.ativo:
                raise ValueError(f"Serviço '{servico.nome}' está inativo e não pode receber preço.")