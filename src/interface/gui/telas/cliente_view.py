"""Tela de gestão de Clientes na GUI: listagem, cadastro, edição e associação de tabela de preço."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QLineEdit, QComboBox, QMessageBox, QHeaderView, QCheckBox
)

from src.dominio.entidades.cliente import Cliente, TipoPessoa
from src.servicos.servico_cliente import ServicoCliente
from src.servicos.servico_tabela_preco import ServicoTabelaPreco


class ClienteView(QWidget):
    def __init__(self, servico: ServicoCliente, servico_tabela_preco: ServicoTabelaPreco) -> None:
        super().__init__()
        self._servico = servico
        self._servico_tabela_preco = servico_tabela_preco
        self._construir_interface()
        self._carregar_clientes()

    def _construir_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        titulo = QLabel("Clientes")
        titulo.setObjectName("titulo")
        titulo.setStyleSheet("padding-bottom: 0px;")
        layout.addWidget(titulo)

        barra_acoes = QHBoxLayout()
        barra_acoes.setSpacing(8)

        botao_novo = QPushButton("+ Novo Cliente")
        botao_novo.clicked.connect(self._abrir_dialogo_novo_cliente)
        barra_acoes.addWidget(botao_novo)

        botao_associar_tabela = QPushButton("Associar Tabela de Preço")
        botao_associar_tabela.setObjectName("botaoSecundario")
        botao_associar_tabela.clicked.connect(self._associar_tabela_preco)
        barra_acoes.addWidget(botao_associar_tabela)

        self._botao_alternar_status = QPushButton("Inativar")
        self._botao_alternar_status.setObjectName("botaoPerigo")
        self._botao_alternar_status.clicked.connect(self._alternar_status_cliente)
        barra_acoes.addWidget(self._botao_alternar_status)

        barra_acoes.addStretch()

        self._checkbox_mostrar_inativos = QCheckBox("Mostrar inativos")
        self._checkbox_mostrar_inativos.stateChanged.connect(self._carregar_clientes)
        barra_acoes.addWidget(self._checkbox_mostrar_inativos)

        layout.addLayout(barra_acoes)

        self._tabela = QTableWidget()
        self._tabela.setColumnCount(7)
        self._tabela.setHorizontalHeaderLabels(
            ["Id", "Nome", "Documento", "E-mail", "Telefone", "Tabela de Preço", "Status"]
        )
        self._tabela.setAlternatingRowColors(True)
        self._tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._tabela.itemSelectionChanged.connect(self._ao_selecionar_cliente)
        layout.addWidget(self._tabela)

    def _carregar_clientes(self) -> None:
        if self._checkbox_mostrar_inativos.isChecked():
            clientes = self._servico.listar_todos_os_clientes()
        else:
            clientes = self._servico.listar_clientes_ativos()

        self._tabela.setRowCount(len(clientes))
        for linha, cliente in enumerate(clientes):
            self._tabela.setItem(linha, 0, QTableWidgetItem(str(cliente.id)))
            self._tabela.setItem(linha, 1, QTableWidgetItem(cliente.nome))
            self._tabela.setItem(linha, 2, QTableWidgetItem(cliente.documento_formatado()))
            self._tabela.setItem(linha, 3, QTableWidgetItem(cliente.email))
            self._tabela.setItem(linha, 4, QTableWidgetItem(cliente.telefone))
            tabela_texto = str(cliente.tabela_preco_id) if cliente.tabela_preco_id else "—"
            self._tabela.setItem(linha, 5, QTableWidgetItem(tabela_texto))
            status_texto = "Ativo" if cliente.ativo else "Inativo"
            self._tabela.setItem(linha, 6, QTableWidgetItem(status_texto))

        self._botao_alternar_status.setText("Inativar")
        self._botao_alternar_status.setEnabled(False)

    def _ao_selecionar_cliente(self) -> None:
        """Ajusta o texto do botão (Inativar/Reativar) conforme o status do cliente selecionado."""
        linha_atual = self._tabela.currentRow()
        if linha_atual < 0:
            self._botao_alternar_status.setEnabled(False)
            return

        status_texto = self._tabela.item(linha_atual, 6).text()
        self._botao_alternar_status.setEnabled(True)
        self._botao_alternar_status.setText("Reativar" if status_texto == "Inativo" else "Inativar")

    def _cliente_selecionado_id(self) -> int | None:
        linha_atual = self._tabela.currentRow()
        if linha_atual < 0:
            QMessageBox.warning(self, "Nenhuma seleção", "Selecione um cliente na tabela primeiro.")
            return None
        return int(self._tabela.item(linha_atual, 0).text())

    def _abrir_dialogo_novo_cliente(self) -> None:
        dialogo = DialogoCliente(self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            dados = dialogo.obter_dados()
            try:
                cliente = Cliente(**dados)
                self._servico.criar_cliente(cliente)
                self._carregar_clientes()
            except ValueError as erro:
                QMessageBox.critical(self, "Erro ao cadastrar", str(erro))

    def _associar_tabela_preco(self) -> None:
        cliente_id = self._cliente_selecionado_id()
        if cliente_id is None:
            return

        tabelas = self._servico_tabela_preco.listar_tabelas_ativas()
        if not tabelas:
            QMessageBox.information(self, "Sem tabelas", "Cadastre uma tabela de preço ativa primeiro.")
            return

        dialogo = DialogoSelecionarTabela(tabelas, self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            try:
                self._servico.associar_tabela_preco(cliente_id, dialogo.tabela_id_selecionada())
                self._carregar_clientes()
            except ValueError as erro:
                QMessageBox.critical(self, "Erro ao associar", str(erro))

    def _alternar_status_cliente(self) -> None:
        cliente_id = self._cliente_selecionado_id()
        if cliente_id is None:
            return

        vai_reativar = self._botao_alternar_status.text() == "Reativar"
        acao_texto = "reativar" if vai_reativar else "inativar"

        resposta = QMessageBox.question(
            self, f"Confirmar {acao_texto}ção" if not vai_reativar else "Confirmar reativação",
            f"Deseja {acao_texto} o cliente id {cliente_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            if vai_reativar:
                self._servico.reativar_cliente(cliente_id)
            else:
                self._servico.inativar_cliente(cliente_id)
            self._carregar_clientes()
        except ValueError as erro:
            QMessageBox.critical(self, "Erro", str(erro))


class DialogoCliente(QDialog):
    """Formulário modal para cadastro de um novo cliente."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Novo Cliente")
        self.setMinimumWidth(400)

        layout = QFormLayout(self)

        self._campo_nome = QLineEdit()
        self._campo_tipo = QComboBox()
        self._campo_tipo.addItem("Pessoa Física", TipoPessoa.FISICA)
        self._campo_tipo.addItem("Pessoa Jurídica", TipoPessoa.JURIDICA)
        self._campo_documento = QLineEdit()
        self._campo_documento.setPlaceholderText("Somente números ou com pontuação")
        self._campo_email = QLineEdit()
        self._campo_telefone = QLineEdit()

        layout.addRow("Nome:", self._campo_nome)
        layout.addRow("Tipo:", self._campo_tipo)
        layout.addRow("CPF/CNPJ:", self._campo_documento)
        layout.addRow("E-mail:", self._campo_email)
        layout.addRow("Telefone:", self._campo_telefone)

        botoes = QHBoxLayout()
        botao_cancelar = QPushButton("Cancelar")
        botao_cancelar.setObjectName("botaoSecundario")
        botao_cancelar.clicked.connect(self.reject)
        botao_salvar = QPushButton("Salvar")
        botao_salvar.clicked.connect(self.accept)
        botoes.addWidget(botao_cancelar)
        botoes.addWidget(botao_salvar)
        layout.addRow(botoes)

    def obter_dados(self) -> dict:
        return {
            "nome": self._campo_nome.text().strip(),
            "tipo_pessoa": self._campo_tipo.currentData(),
            "documento": self._campo_documento.text().strip(),
            "email": self._campo_email.text().strip(),
            "telefone": self._campo_telefone.text().strip(),
        }


class DialogoSelecionarTabela(QDialog):
    """Formulário modal simples para escolher uma tabela de preço de uma lista."""

    def __init__(self, tabelas, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Associar Tabela de Preço")
        self.setMinimumWidth(320)

        layout = QFormLayout(self)
        self._combo = QComboBox()
        for tabela in tabelas:
            self._combo.addItem(tabela.nome, tabela.id)
        layout.addRow("Tabela de preço:", self._combo)

        botoes = QHBoxLayout()
        botao_cancelar = QPushButton("Cancelar")
        botao_cancelar.setObjectName("botaoSecundario")
        botao_cancelar.clicked.connect(self.reject)
        botao_confirmar = QPushButton("Confirmar")
        botao_confirmar.clicked.connect(self.accept)
        botoes.addWidget(botao_cancelar)
        botoes.addWidget(botao_confirmar)
        layout.addRow(botoes)

    def tabela_id_selecionada(self) -> int:
        return self._combo.currentData()