"""ServicoPedidoVenda: cria Pedidos de Venda a partir de Orcamentos aceitos, copiando os
itens como snapshot, e orquestra a máquina de estados de fulfillment."""
from typing import List

from src.dominio.entidades.orcamento import StatusOrcamento
from src.dominio.entidades.pedido_venda import ItemPedidoVenda, PedidoVenda
from src.repositorios.contratos.orcamento_repositorio import OrcamentoRepositorio
from src.repositorios.contratos.pedido_venda_repositorio import PedidoVendaRepositorio


class ServicoPedidoVenda:
    def __init__(
        self, pedido_venda_repositorio: PedidoVendaRepositorio, orcamento_repositorio: OrcamentoRepositorio
    ) -> None:
        self._repositorio = pedido_venda_repositorio
        self._orcamento_repositorio = orcamento_repositorio

    def criar_a_partir_de_orcamento(self, orcamento_id: int) -> PedidoVenda:
        """Gera um Pedido de Venda a partir de um Orçamento ACEITO, copiando seus itens
        ativos como snapshot. Bloqueia se o orçamento não estiver aceito, não tiver itens,
        ou já tiver gerado um pedido antes (idempotência)."""
        orcamento = self._orcamento_repositorio.buscar_por_id(orcamento_id)
        if orcamento is None:
            raise ValueError(f"Orçamento com id {orcamento_id} não encontrado.")

        if orcamento.status != StatusOrcamento.ACEITO:
            raise ValueError(
                f"Só é possível gerar pedido a partir de um orçamento ACEITO. "
                f"Status atual: '{orcamento.status.value}'."
            )

        pedido_existente = self._repositorio.buscar_por_orcamento_id(orcamento_id)
        if pedido_existente is not None:
            raise ValueError(
                f"O orçamento {orcamento_id} já gerou o pedido de venda {pedido_existente.id}. "
                f"Não é possível gerar outro."
            )

        itens_ativos = [item for item in orcamento.itens if item.ativo]
        if not itens_ativos:
            raise ValueError("O orçamento não possui itens ativos para gerar um pedido de venda.")

        itens_do_pedido = [
            ItemPedidoVenda(
                tipo_item=item.tipo_item,
                referencia_id=item.referencia_id,
                descricao=item.descricao,
                preco_unitario=item.preco_unitario,
                quantidade=item.quantidade,
            )
            for item in itens_ativos
        ]

        pedido = PedidoVenda(
            orcamento_id=orcamento_id, cliente_id=orcamento.cliente_id, itens=itens_do_pedido
        )
        return self._repositorio.salvar(pedido)

    def avancar_para_em_separacao(self, pedido_id: int) -> PedidoVenda:
        pedido = self._buscar_ou_lancar_erro(pedido_id)
        pedido.avancar_para_em_separacao()
        return self._repositorio.atualizar(pedido)

    def faturar(self, pedido_id: int) -> PedidoVenda:
        pedido = self._buscar_ou_lancar_erro(pedido_id)
        pedido.faturar()
        return self._repositorio.atualizar(pedido)

    def marcar_como_entregue(self, pedido_id: int) -> PedidoVenda:
        pedido = self._buscar_ou_lancar_erro(pedido_id)
        pedido.marcar_como_entregue()
        return self._repositorio.atualizar(pedido)

    def cancelar(self, pedido_id: int) -> PedidoVenda:
        pedido = self._buscar_ou_lancar_erro(pedido_id)
        pedido.cancelar()
        return self._repositorio.atualizar(pedido)

    def buscar_por_id(self, pedido_id: int) -> PedidoVenda:
        return self._buscar_ou_lancar_erro(pedido_id)

    def listar_por_cliente(self, cliente_id: int) -> List[PedidoVenda]:
        return self._repositorio.listar_por_cliente(cliente_id)

    def listar_todos(self) -> List[PedidoVenda]:
        return self._repositorio.listar_todos()

    def _buscar_ou_lancar_erro(self, pedido_id: int) -> PedidoVenda:
        pedido = self._repositorio.buscar_por_id(pedido_id)
        if pedido is None:
            raise ValueError(f"Pedido de venda com id {pedido_id} não encontrado.")
        return pedido