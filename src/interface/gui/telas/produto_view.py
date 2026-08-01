"""Tela de gestão de Produtos na GUI."""
from decimal import Decimal, InvalidOperation

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QLineEdit, QComboBox, QMessageBox, QHeaderView
)

from src.dominio.entidades.produto import Produto, UnidadeMedida
from src.servicos.servico_produto import ServicoProduto


class ProdutoView(QWidget):
    def __init__(self, servico: ServicoProduto) -> None:
        super().__init__()
        self._servico = servico
        self._construir_interface()
        self._carregar_produtos()

    def _construir_interface(self) -> None:
        layout = QVBoxLayout(self)

        titulo = QLabel("Produtos")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)

        barra_acoes = QHBoxLayout()
        botao_novo = QPushButton("+ Novo Produto")
        botao_novo.clicked.connect(self._abrir_dialogo_novo_produto)
        barra_acoes.addWidget(botao_novo)

        botao_editar_preco = QPushButton("Editar Preço")
        botao_editar_preco.setObjectName("botaoSecundario")
        botao_editar_preco.clicked.connect(self._editar_preco)
        barra_acoes.addWidget(botao_editar_preco)

        botao_inativar = QPushButton("Inativar")
        botao_inativar.setObjectName("botaoPerigo")
        botao_inativar.clicked.connect(self._inativar_produto)
        barra_acoes.addWidget(botao_inativar)

        barra_acoes.addStretch()
        layout.addLayout(barra_acoes)

        self._tabela = QTableWidget()
        self._tabela.setColumnCount(5)
        self._tabela.setHorizontalHeaderLabels(["Id", "Nome", "Unidade", "Preço", "Descrição"])
        self._tabela.setAlternatingRowColors(True)
        self._tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self._tabela)

    def _carregar_produtos(self) -> None:
        produtos = self._servico.listar_produtos_ativos()
        self._tabela.setRowCount(len(produtos))
        for linha, produto in enumerate(produtos):
            self._tabela.setItem(linha, 0, QTableWidgetItem(str(produto.id)))
            self._tabela.setItem(linha, 1, QTableWidgetItem(produto.nome))
            self._tabela.setItem(linha, 2, QTableWidgetItem(produto.unidade_medida.value))
            self._tabela.setItem(linha, 3, QTableWidgetItem(produto.preco_formatado()))
            self._tabela.setItem(linha, 4, QTableWidgetItem(produto.descricao))

    def _produto_selecionado_id(self) -> int | None:
        linha_atual = self._tabela.currentRow()
        if linha_atual < 0:
            QMessageBox.warning(self, "Nenhuma seleção", "Selecione um produto na tabela primeiro.")
            return None
        return int(self._tabela.item(linha_atual, 0).text())

    def _abrir_dialogo_novo_produto(self) -> None:
        dialogo = DialogoProduto(self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            try:
                dados = dialogo.obter_dados()
                produto = Produto(**dados)
                self._servico.criar_produto(produto)
                self._carregar_produtos()
            except (ValueError, InvalidOperation) as erro:
                QMessageBox.critical(self, "Erro ao cadastrar", str(erro))

    def _editar_preco(self) -> None:
        produto_id = self._produto_selecionado_id()
        if produto_id is None:
            return

        produto = self._servico.buscar_por_id(produto_id)
        dialogo = DialogoEditarPreco(produto, self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            try:
                produto.preco_unitario = dialogo.novo_preco()
                self._servico.atualizar_produto(produto)
                self._carregar_produtos()
            except (ValueError, InvalidOperation) as erro:
                QMessageBox.critical(self, "Erro ao atualizar", str(erro))

    def _inativar_produto(self) -> None:
        produto_id = self._produto_selecionado_id()
        if produto_id is None:
            return

        resposta = QMessageBox.question(
            self, "Confirmar inativação",
            f"Deseja inativar o produto id {produto_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            self._servico.inativar_produto(produto_id)
            self._carregar_produtos()
        except ValueError as erro:
            QMessageBox.critical(self, "Erro", str(erro))


class DialogoProduto(QDialog):
    """Formulário modal para cadastro de um novo produto."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Novo Produto")
        self.setMinimumWidth(400)

        layout = QFormLayout(self)

        self._campo_nome = QLineEdit()
        self._campo_unidade = QComboBox()
        for unidade in UnidadeMedida:
            self._campo_unidade.addItem(unidade.value, unidade)
        self._campo_preco = QLineEdit()
        self._campo_preco.setPlaceholderText("Ex: 19.90")
        self._campo_descricao = QLineEdit()

        layout.addRow("Nome:", self._campo_nome)
        layout.addRow("Unidade:", self._campo_unidade)
        layout.addRow("Preço unitário:", self._campo_preco)
        layout.addRow("Descrição:", self._campo_descricao)

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
            "unidade_medida": self._campo_unidade.currentData(),
            "preco_unitario": Decimal(self._campo_preco.text().strip()),
            "descricao": self._campo_descricao.text().strip(),
        }


class DialogoEditarPreco(QDialog):
    """Formulário modal simples para atualizar o preço de um produto existente."""

    def __init__(self, produto: Produto, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Editar Preço — {produto.nome}")
        self.setMinimumWidth(320)

        layout = QFormLayout(self)
        layout.addRow("Preço atual:", QLabel(produto.preco_formatado()))
        self._campo_novo_preco = QLineEdit()
        self._campo_novo_preco.setPlaceholderText("Ex: 25.00")
        layout.addRow("Novo preço:", self._campo_novo_preco)

        botoes = QHBoxLayout()
        botao_cancelar = QPushButton("Cancelar")
        botao_cancelar.setObjectName("botaoSecundario")
        botao_cancelar.clicked.connect(self.reject)
        botao_confirmar = QPushButton("Salvar")
        botao_confirmar.clicked.connect(self.accept)
        botoes.addWidget(botao_cancelar)
        botoes.addWidget(botao_confirmar)
        layout.addRow(botoes)

    def novo_preco(self) -> Decimal:
        return Decimal(self._campo_novo_preco.text().strip())