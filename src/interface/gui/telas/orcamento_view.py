"""Tela de gestão de Orçamentos na GUI: criação, itens, desconto e fluxo de aprovação."""
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QLineEdit, QComboBox, QMessageBox, QHeaderView, QSplitter, QDateEdit,
    QTextEdit
)
from PySide6.QtCore import Qt, QDate

from src.dominio.entidades.tabela_preco import TipoItem
from src.servicos.servico_cliente import ServicoCliente
from src.servicos.servico_orcamento import ServicoOrcamento
from src.servicos.servico_produto import ServicoProduto
from src.servicos.servico_servico import ServicoServico


class OrcamentoView(QWidget):
    def __init__(
        self, servico: ServicoOrcamento, servico_cliente: ServicoCliente,
        servico_produto: ServicoProduto, servico_servico: ServicoServico,
    ) -> None:
        super().__init__()
        self._servico = servico
        self._servico_cliente = servico_cliente
        self._servico_produto = servico_produto
        self._servico_servico = servico_servico
        self._orcamento_id_selecionado: int | None = None
        self._construir_interface()
        self._carregar_orcamentos()

    def _construir_interface(self) -> None:
        layout_geral = QVBoxLayout(self)
        layout_geral.setContentsMargins(16, 16, 16, 16)
        layout_geral.setSpacing(12)

        titulo = QLabel("Orçamentos")
        titulo.setObjectName("titulo")
        titulo.setStyleSheet("padding-bottom: 0px;")
        layout_geral.addWidget(titulo)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Coluna esquerda: lista de orçamentos ---
        coluna_esquerda = QWidget()
        layout_esquerda = QVBoxLayout(coluna_esquerda)
        layout_esquerda.setContentsMargins(0, 0, 0, 0)
        layout_esquerda.setSpacing(8)

        botao_novo = QPushButton("+ Novo Orçamento")
        botao_novo.clicked.connect(self._abrir_dialogo_novo_orcamento)
        layout_esquerda.addWidget(botao_novo)

        self._lista_orcamentos = QTableWidget()
        self._lista_orcamentos.setColumnCount(3)
        self._lista_orcamentos.setHorizontalHeaderLabels(["Id", "Cliente", "Status"])
        self._lista_orcamentos.setAlternatingRowColors(True)
        self._lista_orcamentos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._lista_orcamentos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._lista_orcamentos.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._lista_orcamentos.itemSelectionChanged.connect(self._ao_selecionar_orcamento)
        layout_esquerda.addWidget(self._lista_orcamentos)

        splitter.addWidget(coluna_esquerda)

        # --- Coluna direita: detalhes do orçamento selecionado ---
        coluna_direita = QWidget()
        layout_direita = QVBoxLayout(coluna_direita)
        layout_direita.setContentsMargins(0, 0, 0, 0)
        layout_direita.setSpacing(8)

        self._label_cabecalho = QLabel("Selecione um orçamento à esquerda")
        self._label_cabecalho.setStyleSheet("font-weight: 600; font-size: 14px;")
        layout_direita.addWidget(self._label_cabecalho)

        barra_acoes_item = QHBoxLayout()
        barra_acoes_item.setSpacing(8)
        botao_add_item = QPushButton("+ Item")
        botao_add_item.clicked.connect(self._abrir_dialogo_adicionar_item)
        barra_acoes_item.addWidget(botao_add_item)

        botao_desconto = QPushButton("Aplicar Desconto")
        botao_desconto.setObjectName("botaoSecundario")
        botao_desconto.clicked.connect(self._aplicar_desconto)
        barra_acoes_item.addWidget(botao_desconto)

        botao_anotacao = QPushButton("+ Anotação")
        botao_anotacao.setObjectName("botaoSecundario")
        botao_anotacao.clicked.connect(self._adicionar_anotacao)
        barra_acoes_item.addWidget(botao_anotacao)
        barra_acoes_item.addStretch()
        layout_direita.addLayout(barra_acoes_item)

        self._tabela_itens = QTableWidget()
        self._tabela_itens.setColumnCount(3)
        self._tabela_itens.setHorizontalHeaderLabels(["Item", "Qtd x Preço", "Subtotal"])
        self._tabela_itens.setAlternatingRowColors(True)
        self._tabela_itens.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tabela_itens.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._tabela_itens.setMaximumHeight(180)
        layout_direita.addWidget(self._tabela_itens)

        self._label_totais = QLabel("")
        self._label_totais.setStyleSheet("font-weight: 600;")
        layout_direita.addWidget(self._label_totais)

        barra_acoes_status = QHBoxLayout()
        barra_acoes_status.setSpacing(8)
        self._botao_enviar = QPushButton("Enviar")
        self._botao_enviar.clicked.connect(self._enviar)
        barra_acoes_status.addWidget(self._botao_enviar)

        self._botao_aceitar = QPushButton("Aceitar")
        self._botao_aceitar.clicked.connect(self._aceitar)
        barra_acoes_status.addWidget(self._botao_aceitar)

        self._botao_recusar = QPushButton("Recusar")
        self._botao_recusar.setObjectName("botaoPerigo")
        self._botao_recusar.clicked.connect(self._recusar)
        barra_acoes_status.addWidget(self._botao_recusar)
        barra_acoes_status.addStretch()
        layout_direita.addLayout(barra_acoes_status)

        layout_direita.addWidget(QLabel("Histórico de negociação:"))
        self._texto_historico = QTextEdit()
        self._texto_historico.setReadOnly(True)
        layout_direita.addWidget(self._texto_historico)

        splitter.addWidget(coluna_direita)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout_geral.addWidget(splitter, stretch=1)

    def _carregar_orcamentos(self) -> None:
        orcamentos = self._servico.listar_todos()
        self._lista_orcamentos.setRowCount(len(orcamentos))
        for linha, orcamento in enumerate(orcamentos):
            nome_cliente = self._resolver_nome_cliente(orcamento.cliente_id)
            self._lista_orcamentos.setItem(linha, 0, QTableWidgetItem(str(orcamento.id)))
            self._lista_orcamentos.setItem(linha, 1, QTableWidgetItem(nome_cliente))
            self._lista_orcamentos.setItem(linha, 2, QTableWidgetItem(orcamento.status.value))

    def _resolver_nome_cliente(self, cliente_id: int) -> str:
        try:
            return self._servico_cliente.buscar_por_id(cliente_id).nome
        except ValueError:
            return "(não encontrado)"

    def _ao_selecionar_orcamento(self) -> None:
        linha_atual = self._lista_orcamentos.currentRow()
        if linha_atual < 0:
            return
        self._orcamento_id_selecionado = int(self._lista_orcamentos.item(linha_atual, 0).text())
        self._carregar_detalhes_do_orcamento_selecionado()

    def _carregar_detalhes_do_orcamento_selecionado(self) -> None:
        if self._orcamento_id_selecionado is None:
            return
        orcamento = self._servico.buscar_por_id(self._orcamento_id_selecionado)
        nome_cliente = self._resolver_nome_cliente(orcamento.cliente_id)

        self._label_cabecalho.setText(
            f"Orçamento #{orcamento.id} — {nome_cliente} — status: {orcamento.status.value} — "
            f"validade: {orcamento.data_validade.strftime('%d/%m/%Y')}"
        )

        itens_ativos = [item for item in orcamento.itens if item.ativo]
        self._tabela_itens.setRowCount(len(itens_ativos))
        for linha, item in enumerate(itens_ativos):
            self._tabela_itens.setItem(linha, 0, QTableWidgetItem(item.descricao))
            self._tabela_itens.setItem(
                linha, 1, QTableWidgetItem(f"{item.quantidade} x R$ {item.preco_unitario}")
            )
            self._tabela_itens.setItem(linha, 2, QTableWidgetItem(f"R$ {item.calcular_subtotal()}"))

        self._label_totais.setText(
            f"Subtotal: R$ {orcamento.calcular_subtotal()}   |   "
            f"Desconto ({orcamento.desconto_percentual}%): R$ {orcamento.calcular_valor_desconto()}   |   "
            f"Total: R$ {orcamento.calcular_total()}"
        )

        texto_historico = ""
        for registro in orcamento.historico:
            marca = "🤖" if registro.tipo.value == "AUTOMATICO" else "📝"
            texto_historico += f"{marca} [{registro.data_hora.strftime('%d/%m/%Y %H:%M')}] {registro.descricao}\n"
        self._texto_historico.setPlainText(texto_historico)

        # Botões de ação de status só ficam ativos quando fazem sentido para o status atual
        self._botao_enviar.setEnabled(orcamento.status.value == "RASCUNHO")
        self._botao_aceitar.setEnabled(orcamento.status.value == "ENVIADO")
        self._botao_recusar.setEnabled(orcamento.status.value == "ENVIADO")

    def _abrir_dialogo_novo_orcamento(self) -> None:
        clientes = self._servico_cliente.listar_clientes_ativos()
        if not clientes:
            QMessageBox.information(self, "Sem clientes", "Cadastre um cliente ativo primeiro.")
            return

        dialogo = DialogoNovoOrcamento(clientes, self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            try:
                cliente_id, data_validade = dialogo.obter_dados()
                self._servico.criar_orcamento(cliente_id, data_validade)
                self._carregar_orcamentos()
            except ValueError as erro:
                QMessageBox.critical(self, "Erro ao criar", str(erro))

    def _abrir_dialogo_adicionar_item(self) -> None:
        if not self._exigir_selecao():
            return

        produtos = self._servico_produto.listar_produtos_ativos()
        servicos = self._servico_servico.listar_servicos_ativos()
        dialogo = DialogoAdicionarItemOrcamento(produtos, servicos, self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            try:
                tipo_item, referencia_id, quantidade = dialogo.obter_dados()
                self._servico.adicionar_item(self._orcamento_id_selecionado, tipo_item, referencia_id, quantidade)
                self._carregar_detalhes_do_orcamento_selecionado()
            except (ValueError, InvalidOperation) as erro:
                QMessageBox.critical(self, "Erro ao adicionar item", str(erro))

    def _aplicar_desconto(self) -> None:
        if not self._exigir_selecao():
            return

        dialogo = DialogoDesconto(self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            try:
                self._servico.aplicar_desconto(self._orcamento_id_selecionado, dialogo.percentual())
                self._carregar_detalhes_do_orcamento_selecionado()
            except (ValueError, InvalidOperation) as erro:
                QMessageBox.critical(self, "Erro ao aplicar desconto", str(erro))

    def _adicionar_anotacao(self) -> None:
        if not self._exigir_selecao():
            return

        dialogo = DialogoAnotacao(self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            try:
                self._servico.adicionar_anotacao(self._orcamento_id_selecionado, dialogo.texto())
                self._carregar_detalhes_do_orcamento_selecionado()
            except ValueError as erro:
                QMessageBox.critical(self, "Erro ao adicionar anotação", str(erro))

    def _enviar(self) -> None:
        self._executar_acao_status(self._servico.enviar_orcamento, "enviado")

    def _aceitar(self) -> None:
        self._executar_acao_status(self._servico.aceitar_orcamento, "aceito")

    def _recusar(self) -> None:
        resposta = QMessageBox.question(
            self, "Confirmar recusa", "Deseja recusar este orçamento?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return
        self._executar_acao_status(self._servico.recusar_orcamento, "recusado")

    def _executar_acao_status(self, metodo_servico, particípio: str) -> None:
        if not self._exigir_selecao():
            return
        try:
            metodo_servico(self._orcamento_id_selecionado)
            self._carregar_orcamentos()
            self._carregar_detalhes_do_orcamento_selecionado()
        except ValueError as erro:
            QMessageBox.critical(self, "Erro", str(erro))

    def _exigir_selecao(self) -> bool:
        if self._orcamento_id_selecionado is None:
            QMessageBox.warning(self, "Nenhuma seleção", "Selecione um orçamento à esquerda primeiro.")
            return False
        return True


class DialogoNovoOrcamento(QDialog):
    def __init__(self, clientes, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Novo Orçamento")
        self.setMinimumWidth(380)

        layout = QFormLayout(self)
        self._combo_cliente = QComboBox()
        for cliente in clientes:
            info_tabela = "" if cliente.tabela_preco_id else " (sem tabela de preço!)"
            self._combo_cliente.addItem(f"{cliente.nome}{info_tabela}", cliente.id)
        layout.addRow("Cliente:", self._combo_cliente)

        self._campo_validade = QDateEdit()
        self._campo_validade.setCalendarPopup(True)
        self._campo_validade.setDate(QDate.currentDate().addDays(15))
        layout.addRow("Validade:", self._campo_validade)

        botoes = QHBoxLayout()
        botao_cancelar = QPushButton("Cancelar")
        botao_cancelar.setObjectName("botaoSecundario")
        botao_cancelar.clicked.connect(self.reject)
        botao_salvar = QPushButton("Criar")
        botao_salvar.clicked.connect(self.accept)
        botoes.addWidget(botao_cancelar)
        botoes.addWidget(botao_salvar)
        layout.addRow(botoes)

    def obter_dados(self) -> tuple:
        cliente_id = self._combo_cliente.currentData()
        data_qt = self._campo_validade.date()
        data_validade = date(data_qt.year(), data_qt.month(), data_qt.day())
        return cliente_id, data_validade


class DialogoAdicionarItemOrcamento(QDialog):
    def __init__(self, produtos, servicos, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Adicionar Item ao Orçamento")
        self.setMinimumWidth(400)
        self._produtos = produtos
        self._servicos = servicos

        layout = QFormLayout(self)

        self._campo_tipo = QComboBox()
        self._campo_tipo.addItem("Produto", TipoItem.PRODUTO)
        self._campo_tipo.addItem("Serviço", TipoItem.SERVICO)
        self._campo_tipo.currentIndexChanged.connect(self._atualizar_lista_referencia)
        layout.addRow("Tipo:", self._campo_tipo)

        self._campo_referencia = QComboBox()
        layout.addRow("Item:", self._campo_referencia)
        self._atualizar_lista_referencia()

        self._campo_quantidade = QLineEdit()
        self._campo_quantidade.setPlaceholderText("Ex: 5")
        layout.addRow("Quantidade:", self._campo_quantidade)

        botoes = QHBoxLayout()
        botao_cancelar = QPushButton("Cancelar")
        botao_cancelar.setObjectName("botaoSecundario")
        botao_cancelar.clicked.connect(self.reject)
        botao_salvar = QPushButton("Adicionar")
        botao_salvar.clicked.connect(self.accept)
        botoes.addWidget(botao_cancelar)
        botoes.addWidget(botao_salvar)
        layout.addRow(botoes)

    def _atualizar_lista_referencia(self) -> None:
        self._campo_referencia.clear()
        tipo_selecionado = self._campo_tipo.currentData()
        itens_disponiveis = self._produtos if tipo_selecionado == TipoItem.PRODUTO else self._servicos
        for item in itens_disponiveis:
            self._campo_referencia.addItem(item.nome, item.id)

    def obter_dados(self) -> tuple:
        tipo_item = self._campo_tipo.currentData()
        referencia_id = self._campo_referencia.currentData()
        quantidade = Decimal(self._campo_quantidade.text().strip())
        return tipo_item, referencia_id, quantidade


class DialogoDesconto(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Aplicar Desconto")
        self.setMinimumWidth(320)

        layout = QFormLayout(self)
        self._campo_percentual = QLineEdit()
        self._campo_percentual.setPlaceholderText("Ex: 10")
        layout.addRow("Desconto (%):", self._campo_percentual)

        botoes = QHBoxLayout()
        botao_cancelar = QPushButton("Cancelar")
        botao_cancelar.setObjectName("botaoSecundario")
        botao_cancelar.clicked.connect(self.reject)
        botao_confirmar = QPushButton("Aplicar")
        botao_confirmar.clicked.connect(self.accept)
        botoes.addWidget(botao_cancelar)
        botoes.addWidget(botao_confirmar)
        layout.addRow(botoes)

    def percentual(self) -> Decimal:
        return Decimal(self._campo_percentual.text().strip())


class DialogoAnotacao(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Adicionar Anotação")
        self.setMinimumWidth(400)

        layout = QFormLayout(self)
        self._campo_texto = QTextEdit()
        self._campo_texto.setMaximumHeight(100)
        layout.addRow("Anotação:", self._campo_texto)

        botoes = QHBoxLayout()
        botao_cancelar = QPushButton("Cancelar")
        botao_cancelar.setObjectName("botaoSecundario")
        botao_cancelar.clicked.connect(self.reject)
        botao_confirmar = QPushButton("Adicionar")
        botao_confirmar.clicked.connect(self.accept)
        botoes.addWidget(botao_cancelar)
        botoes.addWidget(botao_confirmar)
        layout.addRow(botoes)

    def texto(self) -> str:
        return self._campo_texto.toPlainText().strip()