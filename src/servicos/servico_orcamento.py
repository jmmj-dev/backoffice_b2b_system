"""ServicoOrcamento: orquestra a criação e gestão de orçamentos, resolvendo preços
a partir da tabela de preço do cliente e mantendo o snapshot de itens congelado."""
from datetime import date
from decimal import Decimal
from typing import List, Optional

from src.dominio.entidades.orcamento import ItemOrcamento, Orcamento
from src.dominio.entidades.tabela_preco import TipoItem
from src.repositorios.contratos.cliente_repositorio import ClienteRepositorio
from src.repositorios.contratos.orcamento_repositorio import OrcamentoRepositorio
from src.repositorios.contratos.produto_repositorio import ProdutoRepositorio
from src.repositorios.contratos.servico_repositorio import ServicoRepositorio
from src.repositorios.contratos.tabela_preco_repositorio import TabelaPrecoRepositorio


class ServicoOrcamento:
    def __init__(
        self,
        orcamento_repositorio: OrcamentoRepositorio,
        cliente_repositorio: ClienteRepositorio,
        tabela_preco_repositorio: TabelaPrecoRepositorio,
        produto_repositorio: ProdutoRepositorio,
        servico_repositorio: ServicoRepositorio,
    ) -> None:
        self._repositorio = orcamento_repositorio
        self._cliente_repositorio = cliente_repositorio
        self._tabela_preco_repositorio = tabela_preco_repositorio
        self._produto_repositorio = produto_repositorio
        self._servico_repositorio = servico_repositorio

    def criar_orcamento(
        self, cliente_id: int, data_validade: date, tabela_preco_id: Optional[int] = None
    ) -> Orcamento:
        """Cria um orçamento em RASCUNHO. Se tabela_preco_id não for informado, usa a tabela
        já associada ao cliente. Se o cliente não tiver tabela e nenhuma for informada, bloqueia."""
        cliente = self._cliente_repositorio.buscar_por_id(cliente_id)
        if cliente is None:
            raise ValueError(f"Cliente com id {cliente_id} não encontrado.")
        if not cliente.ativo:
            raise ValueError(f"Cliente '{cliente.nome}' está inativo. Não é possível criar orçamento.")

        id_tabela = tabela_preco_id or cliente.tabela_preco_id
        if id_tabela is None:
            raise ValueError(
                f"Cliente '{cliente.nome}' não possui tabela de preço associada. "
                f"Informe uma tabela_preco_id explicitamente ou associe uma ao cliente primeiro."
            )

        tabela = self._tabela_preco_repositorio.buscar_por_id(id_tabela)
        if tabela is None:
            raise ValueError(f"Tabela de preço com id {id_tabela} não encontrada.")
        if not tabela.ativa:
            raise ValueError(f"Tabela de preço '{tabela.nome}' está inativa.")

        orcamento = Orcamento(cliente_id=cliente_id, tabela_preco_id=id_tabela, data_validade=data_validade)
        return self._repositorio.salvar(orcamento)

    def adicionar_item(
        self, orcamento_id: int, tipo_item: TipoItem, referencia_id: int, quantidade: Decimal
    ) -> ItemOrcamento:
        """Adiciona um item ao orçamento, buscando o preço na tabela de preço associada
        e congelando (snapshot) o nome e o preço no momento da inclusão."""
        orcamento = self._buscar_ou_lancar_erro(orcamento_id)
        tabela = self._tabela_preco_repositorio.buscar_por_id(orcamento.tabela_preco_id)
        if tabela is None:
            raise ValueError(f"Tabela de preço com id {orcamento.tabela_preco_id} não encontrada.")

        preco = tabela.obter_preco(tipo_item, referencia_id)
        if preco is None:
            raise ValueError(
                f"Não há preço cadastrado para este item na tabela '{tabela.nome}'. "
                f"Cadastre o preço na tabela antes de adicionar ao orçamento."
            )

        descricao = self._resolver_descricao(tipo_item, referencia_id)

        item = orcamento.adicionar_item(
            tipo_item=tipo_item,
            referencia_id=referencia_id,
            descricao=descricao,
            preco_unitario=preco,
            quantidade=quantidade,
        )
        self._repositorio.atualizar(orcamento)
        return item

    def remover_item(self, orcamento_id: int, item_id: int) -> None:
        orcamento = self._buscar_ou_lancar_erro(orcamento_id)
        orcamento.remover_item(item_id)
        self._repositorio.atualizar(orcamento)

    def aplicar_desconto(self, orcamento_id: int, percentual: Decimal) -> Orcamento:
        orcamento = self._buscar_ou_lancar_erro(orcamento_id)
        orcamento.aplicar_desconto(percentual)
        return self._repositorio.atualizar(orcamento)

    def enviar_orcamento(self, orcamento_id: int) -> Orcamento:
        orcamento = self._buscar_ou_lancar_erro(orcamento_id)
        orcamento.enviar()
        return self._repositorio.atualizar(orcamento)

    def aceitar_orcamento(self, orcamento_id: int) -> Orcamento:
        orcamento = self._buscar_ou_lancar_erro(orcamento_id)
        orcamento.verificar_expiracao()
        orcamento.aceitar()
        return self._repositorio.atualizar(orcamento)

    def recusar_orcamento(self, orcamento_id: int) -> Orcamento:
        orcamento = self._buscar_ou_lancar_erro(orcamento_id)
        orcamento.verificar_expiracao()
        orcamento.recusar()
        return self._repositorio.atualizar(orcamento)

    def buscar_por_id(self, orcamento_id: int) -> Orcamento:
        return self._buscar_ou_lancar_erro(orcamento_id)

    def listar_por_cliente(self, cliente_id: int) -> List[Orcamento]:
        return self._repositorio.listar_por_cliente(cliente_id)

    def listar_todos(self) -> List[Orcamento]:
        return self._repositorio.listar_todos()

    def _buscar_ou_lancar_erro(self, orcamento_id: int) -> Orcamento:
        orcamento = self._repositorio.buscar_por_id(orcamento_id)
        if orcamento is None:
            raise ValueError(f"Orçamento com id {orcamento_id} não encontrado.")
        return orcamento

    def _resolver_descricao(self, tipo_item: TipoItem, referencia_id: int) -> str:
        if tipo_item == TipoItem.PRODUTO:
            produto = self._produto_repositorio.buscar_por_id(referencia_id)
            if produto is None:
                raise ValueError(f"Produto com id {referencia_id} não encontrado.")
            return produto.nome
        servico = self._servico_repositorio.buscar_por_id(referencia_id)
        if servico is None:
            raise ValueError(f"Serviço com id {referencia_id} não encontrado.")
        return servico.nome