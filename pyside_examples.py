from PySide2 import QtWidgets, QtCore, QtGui

from rig_builder import build_utils

buttons = {"empty": build_utils.empty_icon,
           "red": build_utils.red_icon,
           "green": build_utils.green_icon,
           "yellow": build_utils.yellow_icon
           }


class stackedExample(QtWidgets.QWidget):
    def __init__(self):
        super(stackedExample, self).__init__()
        self.leftlist = QtWidgets.QListWidget()
        self.leftlist.insertItem(0, 'Contact')
        self.leftlist.insertItem(1, 'Personal')
        self.leftlist.insertItem(2, 'Educational')

        self.stack1 = QtWidgets.QWidget()
        self.stack2 = QtWidgets.QWidget()
        self.stack3 = QtWidgets.QWidget()

        self.stack1UI()
        self.stack2UI()
        self.stack3UI()

        self.Stack = QtWidgets.QStackedWidget(self)
        self.Stack.addWidget(self.stack1)
        self.Stack.addWidget(self.stack2)
        self.Stack.addWidget(self.stack3)

        hbox = QtWidgets.QHBoxLayout(self)
        hbox.addWidget(self.leftlist)
        hbox.addWidget(self.Stack)

        self.setLayout(hbox)
        self.leftlist.currentRowChanged.connect(self.display)
        self.setGeometry(300, 50, 10, 10)
        self.setWindowTitle('StackedWidget Demo')
        self.show()

    def stack1UI(self):
        layout = QtWidgets.QFormLayout()
        layout.addRow("Name", QtWidgets.QLineEdit())
        layout.addRow("Address", QtWidgets.QLineEdit())
        # self.setTabText(0,"Contact Details")
        self.stack1.setLayout(layout)

    def stack2UI(self):
        layout = QtWidgets.QFormLayout()
        sex = QtWidgets.QHBoxLayout()
        sex.addWidget(QtWidgets.QRadioButton("Male"))
        sex.addWidget(QtWidgets.QRadioButton("Female"))
        layout.addRow(QtWidgets.QLabel("Sex"), sex)
        layout.addRow("Date of Birth", QtWidgets.QLineEdit())
        self.stack2.setLayout(layout)

    def stack3UI(self):
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel("subjects"))
        layout.addWidget(QtWidgets.QCheckBox("Physics"))
        layout.addWidget(QtWidgets.QCheckBox("Maths"))
        self.stack3.setLayout(layout)

    def display(self, i):
        self.Stack.setCurrentIndex(i)

    def dragMoveEvent(self, drag_event):
        """
        dragMove event
        :param drag_event:
        :return:
        """
        if drag_event.source() != self:
            drag_event.accept()
        else:
            drag_event.ignore()

# ______________________________________________________________________________________________________________________
# stackedExample.py


class InitialCard(QtWidgets.QLabel):
    def __init__(self, text, parent):
        super(InitialCard, self).__init__(text, parent)
        self.setAutoFillBackground(True)
        self.setFrameStyle(QtWidgets.QFrame.WinPanel | QtWidgets.QFrame.Sunken)
        newFont = QtGui.QFont("MsReferenceSansSerif", 10)
        newFont.setBold(False)
        self.setFont(newFont)
        self.setMinimumSize(90, 25)
        self.setMaximumHeight(30)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.mimeText = self.text()

    def mouseMoveEvent(self, event):
        if not self.text():
            return
        mimeData = QtCore.QMimeData()
        mimeData.setText(self.mimeText)
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction, QtCore.Qt.CopyAction)


class CardsDropWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(CardsDropWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.contentsVLO = QtWidgets.QVBoxLayout()
        self.verify_btn = QtWidgets.QPushButton(self)
        self.verify_btn.setText('verify')
        self.verify_btn.clicked.connect(self.press_event)
        self.contentsVLO.addWidget(self.verify_btn)
        self.contentsVLO.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.contentsVLO)

    def press_event(self):
        print(self.children(), 'children')

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            cardSource = event.source()
            cardText = cardSource.text()
            if cardSource not in self.children():
                newCard = InitialCard(cardText, self)
                self.contentsVLO.addWidget(newCard)
                cardSource.clear()
            else:
                event.ignore()
        else:
            event.ignore()


class MainDialogue(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MainDialogue, self).__init__(parent)
        self.label = InitialCard("initial", self)
        self.lineEdit = QtWidgets.QLineEdit("Create a Card Here!!")
        self.lineEdit.selectAll()
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollContent = CardsDropWidget(self.scrollArea)
        self.scrollArea.setMinimumWidth(150)
        self.scrollArea.setWidget(self.scrollContent)
        self.dialogueLayout = QtWidgets.QHBoxLayout()
        self.labelLayout = QtWidgets.QVBoxLayout()
        self.labelLayout.addWidget(self.label)
        self.labelLayout.addWidget(self.lineEdit)
        self.labelLayout.addStretch()
        self.dialogueLayout.addWidget(self.scrollArea)
        self.dialogueLayout.addLayout(self.labelLayout)
        self.setLayout(self.dialogueLayout)
        self.setWindowTitle("Drag and Drop")
        self.setMinimumSize(300, 150)
        self.lineEdit.returnPressed.connect(self.createCardTxt_fn)

    def createCardTxt_fn(self):
        cardTxt = str(self.lineEdit.text())
        self.label.setText(cardTxt)


class ListModel(QtCore.QAbstractListModel):
    def __init__(self, parent=None):
        QtCore.QAbstractListModel.init(self, parent)
        self._data = ["Row %d" & i for i in range(10)]

    def row_count(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._data)

    def flags(self, index):
        if index.isValid():
            return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEnabled

    def insertRow(self, row, count, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return False
        begin_row = max(0, row)
        end_row = min(row + count-1, len(self._data))
        self.beginInsertRows(parent, begin_row, end_row)
        for i in range(begin_row, end_row+1):
            self._data.insert(i, "")
        self.endInsertRows()
        return True

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid() or role != QtCore.Qt.DisplayRole:
            return False
        self._data[index.row()] = str(value.toString())
        self.dataChanged.emit(index, index)
        return True

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return False
        if row >= len(self._data) or row + count <= 0:
            return False
        beginRow = max(0, row)
        endRow = min(row + count - 1, len(self._data) - 1)
        self.beginRemoveRows(parent, beginRow, endRow)
        for i in range(beginRow, endRow + 1):
            self._data.pop(i)
        self.endRemoveRows()
        return True

#
# ______________________________________________________________________________________________________________________


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.current_index = 0
        self._dropping = False
        # setting title
        self.setWindowTitle("Python")
        # setting geometry
        self.setGeometry(100, 100, 500, 400)
        # calling method
        self.UiComponents()
        # showing all the widgets
        self.show()
        # method for components

    def UiComponents(self):
        # creating a QListWidget
        self.list_widget = QtWidgets.QListWidget(self)
        self.list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.list_widget.setDragEnabled(True)
        self.list_widget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.list_widget.setDropIndicatorShown(True)
        self.list_widget.setDefaultDropAction(QtCore.Qt.MoveAction)
        list_model = self.list_widget.model()
        # setting geometry to it
        self.list_widget.setGeometry(50, 70, 150, 60)
        # list widget items
        item1 = QtWidgets.QListWidgetItem("A")
        item2 = QtWidgets.QListWidgetItem("B")
        item3 = QtWidgets.QListWidgetItem("C")
        # icons
        qpix1 = QtGui.QPixmap(buttons['red'])
        icon1 = QtGui.QIcon(qpix1)
        item1.setIcon(icon1)

        qpix2 = QtGui.QPixmap(buttons['green'])
        icon2 = QtGui.QIcon(qpix2)
        item2.setIcon(icon2)

        qpix3 = QtGui.QPixmap(buttons['green'])
        icon3 = QtGui.QIcon(qpix3)
        item3.setIcon(icon3)
        # adding items to the list widget
        self.list_widget.addItem(item1)
        self.list_widget.addItem(item2)
        self.list_widget.addItem(item3)
        # setting drag drop mode
        self.list_widget.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        # creating a label
        label = QtWidgets.QLabel("GeeksForGeeks", self)
        # setting geometry to the label
        label.setGeometry(230, 80, 280, 80)
        # making label multi line
        label.setWordWrap(True)
        # getting drag drop property
        value = self.list_widget.dragDropMode()
        # setting text to the label
        label.setText("Drag Drop Property : " + str(value))
        list_model.rowsInserted.connect(self.on_rowsInserted)
        list_model.rowsRemoved.connect(self.on_rowsRemoved)
        self.list_widget.itemClicked.connect(self.on_index)

    def check_list_length(self):
        print(self.list_widget.count())

    def on_index(self, widget_item):
        # self.list_widget.selectionModel().selectedIndexes()
        self.current_index = self.list_widget.currentRow()
        print(self.current_index, widget_item.text())

    def on_rowsRemoved(*args):
        print(args)

    def on_rowsInserted(self, parent_index, start, end):
        self.current_index = self.list_widget.currentRow()
        print('cur_index', self.current_index)
        print(type(parent_index), '<--', start, end)

# ______________________________________________________________________________________________________________________
# pyside_examples.py
