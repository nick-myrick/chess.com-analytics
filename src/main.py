import sys
from pathlib import Path

import dask.dataframe as dd

import load_data
import widgets.add_widgets as add_widgets

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel

dfs = dict[str, dd.DataFrame]

'''
Runs the main PyQt6 Window and adds of the necessary widgets and update functions
'''

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

        # Loop through the widgets in the first column and center them vertically
        for row in range(self.layout.rowCount()):
            widget_item = self.layout.itemAtPosition(row, 0)
            if widget_item:
                widget = widget_item.widget()  # Extract the widget from QLayoutItem
                if widget:
                    self.layout.setAlignment(widget, Qt.AlignmentFlag.AlignVCenter)  # Center the widget vertically
    
    def setup_window(self):
        '''
        Set initial window settings
        '''
        self.width = 1920
        self.height = 1920
        self.setGeometry(100, 100, self.width, self.height)
        self.resize(1920, 1920)
        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QtWidgets.QGridLayout(self.main_widget)
        #self.setStyleSheet("background-color: #2c2b29")
        self.setStyleSheet("background-color: #000000")

        #self.layout.setHorizontalSpacing(100) 
        self.layout.setContentsMargins(20, 10, 20, 10)

        self.layout.setHorizontalSpacing(10)        # Horizontal spacing between columns
        #self.layout.setVerticalSpacing(5) 

        self.layout.setColumnStretch(0, 2)  # Column 0 gets 1 part of the space
        self.layout.setColumnStretch(1, 3)

        self.setWindowTitle("Chess.com Analytics")
        label = QLabel("Chess.com Analytics")
        label.setStyleSheet("""
            font-size: 70px;
            font-weight: bold;
            color: #eeeed2;
            padding-top: 20px;
            padding-bottom: 20px;
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