"""Tela de gestão de Tabelas de Preço na GUI, incluindo os itens (produtos/serviços) de cada tabela."""
from decimal import Decimal, InvalidOperation

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QLineEdit, QComboBox, QMessageBox, QHeaderView, QSplitter
)
from PySide6.QtCore import Qt

from src.dominio.entidades.tabela_preco import TabelaPreco, TipoItem
from src.servicos.servico_produto import ServicoProduto
from src.servicos.servico_servico import ServicoServico
from src.servicos.servico_tabela_preco import ServicoTabelaPreco


class TabelaPrecoView(QWidget):
    def __init__(
        self, servico: ServicoTabelaPreco, servico_produto: ServicoProduto, servico_servico: ServicoServico
    ) -> None:
        super().__init__()
        self._servico = servico
        self._servico_produto = servico_produto
        self._servico_servico = servico_servico
        self._tabela_id_selecionada: int | None = None
        self._construir_interface()
        self._carregar_tabelas()

    def _construir_interface(self) -> None:
        layout_geral = QVBoxLayout(self)
        layout_geral.setContentsMargins(16, 16, 16, 16)
        layout_geral.setSpacing(12)

        titulo = QLabel("Tabelas de Preço")
        titulo.setObjectName("titulo")
        titulo.setStyleSheet("padding-bottom: 0px;")  # remove o respiro extra do tema global aqui
        layout_geral.addWidget(titulo)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Coluna esquerda: lista de tabelas ---
        coluna_esquerda = QWidget()
        layout_esquerda = QVBoxLayout(coluna_esquerda)
        layout_esquerda.setContentsMargins(0, 0, 0, 0)
        layout_esquerda.setSpacing(8)

        botao_nova_tabela = QPushButton("+ Nova Tabela")
        botao_nova_tabela.clicked.connect(self._abrir_dialogo_nova_tabela)
        layout_esquerda.addWidget(botao_nova_tabela)

        self._lista_tabelas = QTableWidget()
        self._lista_tabelas.setColumnCount(2)
        self._lista_tabelas.setHorizontalHeaderLabels(["Id", "Nome"])
        self._lista_tabelas.setAlternatingRowColors(True)
        self._lista_tabelas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._lista_tabelas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._lista_tabelas.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._lista_tabelas.itemSelectionChanged.connect(self._ao_selecionar_tabela)
        layout_esquerda.addWidget(self._lista_tabelas)

        splitter.addWidget(coluna_esquerda)

        # --- Coluna direita: itens da tabela selecionada ---
        coluna_direita = QWidget()
        layout_direita = QVBoxLayout(coluna_direita)
        layout_direita.setContentsMargins(0, 0, 0, 0)
        layout_direita.setSpacing(8)

        self._label_tabela_atual = QLabel("Selecione uma tabela à esquerda")
        self._label_tabela_atual.setStyleSheet("font-weight: 600; font-size: 14px;")
        layout_direita.addWidget(self._label_tabela_atual)

        barra_acoes_item = QHBoxLayout()
        barra_acoes_item.setSpacing(8)
        botao_add_item = QPushButton("+ Adicionar Item")
        botao_add_item.clicked.connect(self._abrir_dialogo_adicionar_item)
        barra_acoes_item.addWidget(botao_add_item)

        botao_remover_item = QPushButton("Remover Item")
        botao_remover_item.setObjectName("botaoPerigo")
        botao_remover_item.clicked.connect(self._remover_item)
        barra_acoes_item.addWidget(botao_remover_item)
        barra_acoes_item.addStretch()
        layout_direita.addLayout(barra_acoes_item)

        self._tabela_itens = QTableWidget()
        self._tabela_itens.setColumnCount(4)
        self._tabela_itens.setHorizontalHeaderLabels(["Tipo", "Id Referência", "Item", "Preço"])
        self._tabela_itens.setAlternatingRowColors(True)
        self._tabela_itens.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._tabela_itens.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tabela_itens.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        layout_direita.addWidget(self._tabela_itens)

        splitter.addWidget(coluna_direita)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout_geral.addWidget(splitter, stretch=1)

    def _carregar_tabelas(self) -> None:
        tabelas = self._servico.listar_tabelas_ativas()
        self._lista_tabelas.setRowCount(len(tabelas))
        for linha, tabela in enumerate(tabelas):
            self._lista_tabelas.setItem(linha, 0, QTableWidgetItem(str(tabela.id)))
            self._lista_tabelas.setItem(linha, 1, QTableWidgetItem(tabela.nome))

    def _ao_selecionar_tabela(self) -> None:
        linha_atual = self._lista_tabelas.currentRow()
        if linha_atual < 0:
            return
        self._tabela_id_selecionada = int(self._lista_tabelas.item(linha_atual, 0).text())
        self._carregar_itens_da_tabela_selecionada()

    def _carregar_itens_da_tabela_selecionada(self) -> None:
        if self._tabela_id_selecionada is None:
            return
        tabela = self._servico.buscar_por_id(self._tabela_id_selecionada)
        self._label_tabela_atual.setText(f"Itens de: {tabela.nome}")

        itens_ativos = [item for item in tabela.itens if item.ativo]
        self._tabela_itens.setRowCount(len(itens_ativos))
        for linha, item in enumerate(itens_ativos):
            nome_item = self._resolver_nome_item(item.tipo_item, item.referencia_id)
            self._tabela_itens.setItem(linha, 0, QTableWidgetItem(item.tipo_item.value))
            self._tabela_itens.setItem(linha, 1, QTableWidgetItem(str(item.referencia_id)))
            self._tabela_itens.setItem(linha, 2, QTableWidgetItem(nome_item))
            self._tabela_itens.setItem(linha, 3, QTableWidgetItem(f"R$ {item.preco}"))

    def _resolver_nome_item(self, tipo_item: TipoItem, referencia_id: int) -> str:
        try:
            if tipo_item == TipoItem.PRODUTO:
                return self._servico_produto.buscar_por_id(referencia_id).nome
            return self._servico_servico.buscar_por_id(referencia_id).nome
        except ValueError:
            return "(não encontrado)"

    def _abrir_dialogo_nova_tabela(self) -> None:
        dialogo = DialogoNovaTabela(self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            try:
                self._servico.criar_tabela(TabelaPreco(**dialogo.obter_dados()))
                self._carregar_tabelas()
            except ValueError as erro:
                QMessageBox.critical(self, "Erro ao criar", str(erro))

    def _abrir_dialogo_adicionar_item(self) -> None:
        if self._tabela_id_selecionada is None:
            QMessageBox.warning(self, "Nenhuma tabela", "Selecione uma tabela de preço primeiro.")
            return

        produtos = self._servico_produto.listar_produtos_ativos()
        servicos = self._servico_servico.listar_servicos_ativos()
        dialogo = DialogoAdicionarItem(produtos, servicos, self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            try:
                tipo_item, referencia_id, preco = dialogo.obter_dados()
                self._servico.adicionar_item(self._tabela_id_selecionada, tipo_item, referencia_id, preco)
                self._carregar_itens_da_tabela_selecionada()
            except (ValueError, InvalidOperation) as erro:
                QMessageBox.critical(self, "Erro ao adicionar item", str(erro))

    def _remover_item(self) -> None:
        if self._tabela_id_selecionada is None:
            return
        linha_atual = self._tabela_itens.currentRow()
        if linha_atual < 0:
            QMessageBox.warning(self, "Nenhuma seleção", "Selecione um item na tabela primeiro.")
            return

        tipo_item = TipoItem(self._tabela_itens.item(linha_atual, 0).text())
        referencia_id = int(self._tabela_itens.item(linha_atual, 1).text())

        try:
            self._servico.remover_item(self._tabela_id_selecionada, tipo_item, referencia_id)
            self._carregar_itens_da_tabela_selecionada()
        except ValueError as erro:
            QMessageBox.critical(self, "Erro ao remover", str(erro))


class DialogoNovaTabela(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nova Tabela de Preço")
        self.setMinimumWidth(360)

        layout = QFormLayout(self)
        self._campo_nome = QLineEdit()
        self._campo_descricao = QLineEdit()
        layout.addRow("Nome:", self._campo_nome)
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
            "descricao": self._campo_descricao.text().strip(),
        }


class DialogoAdicionarItem(QDialog):
    """Formulário modal para adicionar um produto ou serviço, com preço, a uma tabela."""

    def __init__(self, produtos, servicos, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Adicionar Item à Tabela")
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

        self._campo_preco = QLineEdit()
        self._campo_preco.setPlaceholderText("Ex: 45.00")
        layout.addRow("Preço nesta tabela:", self._campo_preco)

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
        preco = Decimal(self._campo_preco.text().strip())
        return tipo_item, referencia_id, preco