# Standard
import sys
from pathlib import Path

# Custom
import load_data
import widgets.add_widgets as add_widgets

# UI
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel

dfs = None

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        '''
        Initialize the window, then add the player, gm, and tt widgets
        '''
        super().__init__()
        self.setup_window()

        add_widgets.add_player_widgets(self, dfs)
        add_widgets.add_gm_widgets(self, dfs)
        add_widgets.add_titled_tuesday_widgets(self, dfs)
    
    def setup_window(self):
        '''
        Set initial window settings
        '''
        self.width = 1920
        self.height = 1920
        self.setGeometry(100, 100, self.width, self.height)
        #self.setFixedSize(self.width, self.height)
        self.resize(1920, 1920)
        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QtWidgets.QGridLayout(self.main_widget)
        self.setStyleSheet("background-color: #2c2b29")

        self.layout.setHorizontalSpacing(100) 
        self.layout.setContentsMargins(20, 10, 20, 10)

        self.layout.setColumnStretch(0, 2)  # Column 0 gets 1 part of the space
        self.layout.setColumnStretch(1, 3)

        self.setWindowTitle("Chess.com Statistics")
        label = QLabel("Chess.com Statistics")
        label.setStyleSheet("""
            font-size: 45px;
            font-weight: bold;
            color: #eeeed2;
            padding-top: 20px;
            padding-bottom: 20px;
            text-decoration: underline;
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(label, 0, 0, 1, 3)

def main():
    '''
    Load dataframes and start the application!
    '''
    global dfs
    dfs = load_data.load(dfs)
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()

if __name__ == "__main__":
    main()