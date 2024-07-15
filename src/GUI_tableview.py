from PyQt5.Qt import Qt
from PyQt5.QtWidgets import QTableView, QApplication, QWidget, QVBoxLayout, QStyledItemDelegate, QHeaderView
from PyQt5.QtCore import QAbstractTableModel
import pandas as pd

class PandasModel(QAbstractTableModel):
    def __init__(self, data=pd.DataFrame()):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.index)

    def columnCount(self, parent=None):
        return len(self._data.columns)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            try:
                return self._data.columns.tolist()[section]
            except (IndexError, ):
                return None
        elif orientation == Qt.Vertical:
            try:
                return self._data.index.tolist()[section]
            except (IndexError, ):
                return None

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            try:
                return str(self._data.iloc[index.row(), index.column()])
            except (IndexError, ):
                return None
        return None

class Table(QWidget):
    def __init__(self, model):
        super().__init__()
        self.model = model

        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        # self.table_view.setSortingEnabled(True)
        self.table_view.setAlternatingRowColors(True)
        # table context central
        self.table_view.setItemDelegate(CenterAlignmentDelegate())

        self.table_view.horizontalHeader().setStyleSheet("border: 0.5px solid rgb(210, 210, 210)")
        self.table_view.verticalHeader().setStyleSheet("border: 0.5px solid rgb(210, 210, 210)")

        layout = QVBoxLayout()
        layout.addWidget(self.table_view)

        self.setLayout(layout)

class CenterAlignmentDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignCenter
        super().paint(painter, option, index)

# if __name__ == '__main__':
#     app = QApplication([])
#
#     # create sample data
#     data = pd.read_csv('E:/working/data_process/data/result/cpt0870.mmp1')
#
#     # create and show widget
#     model = PandasModel(data)
#     table = Table(model)
#     table.show()
#
#     app.exec_()