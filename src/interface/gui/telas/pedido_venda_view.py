"""Tela de gestão de Pedidos de Venda na GUI: geração a partir de orçamento aceito
e acompanhamento do fluxo de fulfillment."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QComboBox, QMessageBox, QHeaderView, QSplitter
)
from PySide6.QtCore import Qt

from src.servicos.servico_cliente import ServicoCliente
from src.servicos.servico_orcamento import ServicoOrcamento
from src.servicos.servico_pedido_venda import ServicoPedidoVenda


class PedidoVendaView(QWidget):
    def __init__(
        self, servico: ServicoPedidoVenda, servico_orcamento: ServicoOrcamento, servico_cliente: ServicoCliente,
    ) -> None:
        super().__init__()
        self._servico = servico
        self._servico_orcamento = servico_orcamento
        self._servico_cliente = servico_cliente
        self._pedido_id_selecionado: int | None = None
        self._construir_interface()
        self._carregar_pedidos()

    def _construir_interface(self) -> None:
        layout_geral = QVBoxLayout(self)
        layout_geral.setContentsMargins(16, 16, 16, 16)
        layout_geral.setSpacing(12)

        titulo = QLabel("Pedidos de Venda")
        titulo.setObjectName("titulo")
        titulo.setStyleSheet("padding-bottom: 0px;")
        layout_geral.addWidget(titulo)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Coluna esquerda: lista de pedidos ---
        coluna_esquerda = QWidget()
        layout_esquerda = QVBoxLayout(coluna_esquerda)
        layout_esquerda.setContentsMargins(0, 0, 0, 0)
        layout_esquerda.setSpacing(8)

        botao_gerar = QPushButton("+ Gerar de Orçamento Aceito")
        botao_gerar.clicked.connect(self._abrir_dialogo_gerar_pedido)
        layout_esquerda.addWidget(botao_gerar)

        self._lista_pedidos = QTableWidget()
        self._lista_pedidos.setColumnCount(3)
        self._lista_pedidos.setHorizontalHeaderLabels(["Id", "Cliente", "Status"])
        self._lista_pedidos.setAlternatingRowColors(True)
        self._lista_pedidos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._lista_pedidos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._lista_pedidos.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._lista_pedidos.itemSelectionChanged.connect(self._ao_selecionar_pedido)
        layout_esquerda.addWidget(self._lista_pedidos)

        splitter.addWidget(coluna_esquerda)

        # --- Coluna direita: detalhes do pedido selecionado ---
        coluna_direita = QWidget()
        layout_direita = QVBoxLayout(coluna_direita)
        layout_direita.setContentsMargins(0, 0, 0, 0)
        layout_direita.setSpacing(8)

        self._label_cabecalho = QLabel("Selecione um pedido à esquerda")
        self._label_cabecalho.setStyleSheet("font-weight: 600; font-size: 14px;")
        layout_direita.addWidget(self._label_cabecalho)

        self._tabela_itens = QTableWidget()
        self._tabela_itens.setColumnCount(3)
        self._tabela_itens.setHorizontalHeaderLabels(["Item", "Qtd x Preço", "Subtotal"])
        self._tabela_itens.setAlternatingRowColors(True)
        self._tabela_itens.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tabela_itens.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        layout_direita.addWidget(self._tabela_itens)

        self._label_total = QLabel("")
        self._label_total.setStyleSheet("font-weight: 600;")
        layout_direita.addWidget(self._label_total)

        barra_acoes_status = QHBoxLayout()
        barra_acoes_status.setSpacing(8)

        self._botao_em_separacao = QPushButton("Em Separação")
        self._botao_em_separacao.clicked.connect(self._avancar_em_separacao)
        barra_acoes_status.addWidget(self._botao_em_separacao)

        self._botao_faturar = QPushButton("Faturar")
        self._botao_faturar.clicked.connect(self._faturar)
        barra_acoes_status.addWidget(self._botao_faturar)

        self._botao_entregar = QPushButton("Marcar Entregue")
        self._botao_entregar.clicked.connect(self._marcar_entregue)
        barra_acoes_status.addWidget(self._botao_entregar)

        self._botao_cancelar = QPushButton("Cancelar")
        self._botao_cancelar.setObjectName("botaoPerigo")
        self._botao_cancelar.clicked.connect(self._cancelar)
        barra_acoes_status.addWidget(self._botao_cancelar)

        barra_acoes_status.addStretch()
        layout_direita.addLayout(barra_acoes_status)
        layout_direita.addStretch()

        splitter.addWidget(coluna_direita)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout_geral.addWidget(splitter, stretch=1)

    def _carregar_pedidos(self) -> None:
        pedidos = self._servico.listar_todos()
        self._lista_pedidos.setRowCount(len(pedidos))
        for linha, pedido in enumerate(pedidos):
            nome_cliente = self._resolver_nome_cliente(pedido.cliente_id)
            self._lista_pedidos.setItem(linha, 0, QTableWidgetItem(str(pedido.id)))
            self._lista_pedidos.setItem(linha, 1, QTableWidgetItem(nome_cliente))
            self._lista_pedidos.setItem(linha, 2, QTableWidgetItem(pedido.status.value))

    def _resolver_nome_cliente(self, cliente_id: int) -> str:
        try:
            return self._servico_cliente.buscar_por_id(cliente_id).nome
        except ValueError:
            return "(não encontrado)"

    def _ao_selecionar_pedido(self) -> None:
        linha_atual = self._lista_pedidos.currentRow()
        if linha_atual < 0:
            return
        self._pedido_id_selecionado = int(self._lista_pedidos.item(linha_atual, 0).text())
        self._carregar_detalhes_do_pedido_selecionado()

    def _carregar_detalhes_do_pedido_selecionado(self) -> None:
        if self._pedido_id_selecionado is None:
            return
        pedido = self._servico.buscar_por_id(self._pedido_id_selecionado)
        nome_cliente = self._resolver_nome_cliente(pedido.cliente_id)

        self._label_cabecalho.setText(
            f"Pedido #{pedido.id} — {nome_cliente} — status: {pedido.status.value} — "
            f"origem: orçamento #{pedido.orcamento_id}"
        )

        self._tabela_itens.setRowCount(len(pedido.itens))
        for linha, item in enumerate(pedido.itens):
            self._tabela_itens.setItem(linha, 0, QTableWidgetItem(item.descricao))
            self._tabela_itens.setItem(
                linha, 1, QTableWidgetItem(f"{item.quantidade} x R$ {item.preco_unitario}")
            )
            self._tabela_itens.setItem(linha, 2, QTableWidgetItem(f"R$ {item.calcular_subtotal()}"))

        self._label_total.setText(f"Total: R$ {pedido.calcular_total()}")

        status = pedido.status.value
        self._botao_em_separacao.setEnabled(status == "PENDENTE")
        self._botao_faturar.setEnabled(status == "EM_SEPARACAO")
        self._botao_entregar.setEnabled(status == "FATURADO")
        self._botao_cancelar.setEnabled(status in ("PENDENTE", "EM_SEPARACAO", "FATURADO"))

    def _abrir_dialogo_gerar_pedido(self) -> None:
        orcamentos_aceitos = [
            o for o in self._servico_orcamento.listar_todos() if o.status.value == "ACEITO"
        ]
        if not orcamentos_aceitos:
            QMessageBox.information(self, "Sem orçamentos aceitos", "Nenhum orçamento com status ACEITO disponível.")
            return

        dialogo = DialogoGerarPedido(orcamentos_aceitos, self._servico_cliente, self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            try:
                self._servico.criar_a_partir_de_orcamento(dialogo.orcamento_id_selecionado())
                self._carregar_pedidos()
            except ValueError as erro:
                QMessageBox.critical(self, "Erro ao gerar pedido", str(erro))

    def _avancar_em_separacao(self) -> None:
        self._executar_acao_status(self._servico.avancar_para_em_separacao)

    def _faturar(self) -> None:
        self._executar_acao_status(self._servico.faturar)

    def _marcar_entregue(self) -> None:
        resposta = QMessageBox.question(
            self, "Confirmar entrega", "Confirma que este pedido foi entregue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return
        self._executar_acao_status(self._servico.marcar_como_entregue)

    def _cancelar(self) -> None:
        resposta = QMessageBox.question(
            self, "Confirmar cancelamento", "Deseja cancelar este pedido?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return
        self._executar_acao_status(self._servico.cancelar)

    def _executar_acao_status(self, metodo_servico) -> None:
        if self._pedido_id_selecionado is None:
            QMessageBox.warning(self, "Nenhuma seleção", "Selecione um pedido à esquerda primeiro.")
            return
        try:
            metodo_servico(self._pedido_id_selecionado)
            self._carregar_pedidos()
            self._carregar_detalhes_do_pedido_selecionado()
        except ValueError as erro:
            QMessageBox.critical(self, "Erro", str(erro))


class DialogoGerarPedido(QDialog):
    """Formulário modal para escolher um orçamento ACEITO e gerar o pedido de venda a partir dele."""

    def __init__(self, orcamentos_aceitos, servico_cliente: ServicoCliente, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Gerar Pedido de Venda")
        self.setMinimumWidth(380)

        layout = QFormLayout(self)
        self._combo_orcamento = QComboBox()
        for orcamento in orcamentos_aceitos:
            try:
                nome_cliente = servico_cliente.buscar_por_id(orcamento.cliente_id).nome
            except ValueError:
                nome_cliente = "(não encontrado)"
            self._combo_orcamento.addItem(f"#{orcamento.id} — {nome_cliente}", orcamento.id)
        layout.addRow("Orçamento aceito:", self._combo_orcamento)

        botoes = QHBoxLayout()
        botao_cancelar = QPushButton("Cancelar")
        botao_cancelar.setObjectName("botaoSecundario")
        botao_cancelar.clicked.connect(self.reject)
        botao_confirmar = QPushButton("Gerar Pedido")
        botao_confirmar.clicked.connect(self.accept)
        botoes.addWidget(botao_cancelar)
        botoes.addWidget(botao_confirmar)
        layout.addRow(botoes)

    def orcamento_id_selecionado(self) -> int:
        return self._combo_orcamento.currentData()