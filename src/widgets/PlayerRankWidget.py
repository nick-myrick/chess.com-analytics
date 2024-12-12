from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class PlayerRankWidget(QWidget):
    player_selected = pyqtSignal(int)
    def __init__(self, player_data):
        super().__init__()
        self.setWindowTitle("Player Rankings")

        # Main layout
        layout = QVBoxLayout(self)

        # Create a table widget
        self.table = QTableWidget()
        self.table.setColumnCount(3)  # Two columns: Ranking and Name
        self.table.setHorizontalHeaderLabels(["Rank", "Player Name", "#Wins"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Make it non-editable
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)  # Row-based selection
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)  # Single row selection

        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.verticalHeader().hide()

        font = QFont("Arial", 15)  # Font: Arial, Size: 12
        self.table.setFont(font) 
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Center align all cell contents
        for i in range(self.table.columnCount()):
            self.table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignmentFlag.AlignCenter)



        # Populate the table with player data
        self.table.setRowCount(len(player_data))
        for row, (ranking, name, wins) in enumerate(player_data):
            self.table.setItem(row, 0, QTableWidgetItem(str(ranking)))  # Ranking column
            self.table.setItem(row, 1, QTableWidgetItem(name))  # Player Name column
            self.table.setItem(row, 2, QTableWidgetItem(str(wins)))  # Number of Wins column
            # Center align all cell contents
            for col in range(self.table.columnCount()):
                cell_item = self.table.item(row, col)
                if cell_item is not None:
                    cell_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)


        # Connect a click event
        self.table.cellClicked.connect(self.on_name_clicked)

        # Add the table to the layout
        layout.addWidget(self.table)

    def on_name_clicked(self, row, column):
        # Get the player's name from the second column
        self.player_selected.emit(row)