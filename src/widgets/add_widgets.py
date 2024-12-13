from typing import Self

import plotting.player_plots as player_plots
import plotting.gm_plots as gm_plots
import plotting.titled_tuesday_plots as titled_tuesday_plots
import constants

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
import dask.dataframe as dd

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QLabel, QWidget, QHBoxLayout, QVBoxLayout
from widgets.QRangeSlider import *
from widgets.PlayerRankWidget import *

'''
Functions that add the relevant widgets to the PyQt6 Window.
These widgets can be defined into 3 subcategories:
    1) Player Widgets
    2) Grandmaster Widgets
    3) Titled Tuesday Widgets
'''

def add_player_widgets(
        self: Self,
        dfs: dict[str, dd.DataFrame]) -> None:
    '''
    Info:
    Creates the player widgets to display
        1) Glicko score trend with time control and date range selection
        2) Winning prediction probabilities vs. lower rated opponents

    Parameters:
    - self (Self): The instance of the QMainWindow so we can write the widgets directly to its main layout
    - dfs (dict[str, dd.DataFrame]): The dictionary of dask dataframes which contains our player data

    Returns:
    - None
    '''
    
    player_vbox = QVBoxLayout()
    #player_vbox.addStretch()
    '''
    Single column, 5 rows. Left half of the screen
    '''
    self.start_year = 2008
    self.end_year = 2023 
    self.time_control = "10 min"
    self.gm = 'hikaru'

    # Title
    label = QLabel("General Player Statistics")
    label.setStyleSheet("""
        font-size: 55px;
        font-weight: bold;
        color: #81b64c;
        padding-top: 20px;
        padding-bottom: 20px;
    """)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    player_vbox.addWidget(label)
    #self.layout.addWidget(label, 1, 0)

    # Accuracy canvas
    label = QLabel("Median Player Glicko Trend")
    label.setStyleSheet("""
        font-size: 30px;
        font-weight: bold;
        color: #ebecd0;
        padding-top: 20px;
        padding-bottom: 20px;
    """)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    #self.layout.addWidget(label, 2, 0)
    player_vbox.addWidget(label)
    self.player_accu_figure = Figure()
    self.player_accu_figure.subplots_adjust(bottom=0.2)
    self.player_accu_canvas = FigureCanvas(self.player_accu_figure) # fig size in inches
    player_plots.create_player_accuracy_trend_plot(self.player_accu_canvas.figure.subplots(), dfs, self.start_year, self.end_year, self.time_control)
    player_vbox.addWidget(self.player_accu_canvas)
    #self.layout.addWidget(self.player_accu_canvas, 3, 0)


    # Time Control Selection
    time_control_layout = QHBoxLayout()
    label = QLabel("Time Control:")
    label.setStyleSheet("""
        font-size: 25px;
        font-weight: bold;
        color: #bdc4b4;
    """)
    time_control_layout.addWidget(label)

    self.time_control_box = QComboBox(self.main_widget)
    self.time_control_box.addItems(constants.TIME_CONTROLS)
    self.time_control_box.setStyleSheet("""
        QComboBox {
            padding: 10px;
            margin: 5px;
            max-width: 200px; /* Prevent stretching */
            font-size: 25px;
        }
    """)
    time_control_layout.addWidget(self.time_control_box)
    self.time_control_box.currentIndexChanged.connect(lambda idx: time_control_update(self, idx, dfs))
    self.time_control_box.setCurrentIndex(constants.TIME_CONTROLS.index(self.time_control))

    year_range_layout = QVBoxLayout()
    # Year range selection
    self.year_range_label = QLabel(f"Year range: {self.start_year} - {self.end_year}")
    self.year_range_label.setStyleSheet("""
        font-size: 25px;
        font-weight: bold;
        color: #bdc4b4;
    """)
    self.year_range_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    year_range_layout.addWidget(self.year_range_label)

    self.range_slider = QRangeSlider(self, self.start_year, self.end_year)
    year_range_layout.addWidget(self.range_slider)
    self.range_slider.rangeChanged.connect(lambda x, y: update_player_plots(self, x, y, dfs))
    self.range_slider.update = update_year_range_label

    time_control_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    containerLayout = QHBoxLayout()
    containerLayout.addLayout(time_control_layout)
    containerLayout.addLayout(year_range_layout)
    containerLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    player_vbox.addLayout(containerLayout)

    # Winning chances canvas
    label = QLabel("Winning Odds v.s. Opponent ~100 Points Lower")
    label.setStyleSheet("""
        font-size: 30px;
        font-weight: bold;
        color: #ebecd0;
        padding-top: 20px;
        padding-bottom: 20px;
    """)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    player_vbox.addWidget(label)
    self.player_win_chance_figure = Figure()
    self.player_win_chance_figure.subplots_adjust(bottom=0.2)
    self.player_win_chance_canvas = FigureCanvas(self.player_win_chance_figure) # fig size in inches
    player_plots.create_player_elo_odds_plot(self.player_win_chance_canvas.figure.subplots(), dfs)
    player_vbox.addWidget(self.player_win_chance_canvas)

    self.layout.addLayout(player_vbox, 1, 0, 7, 1)
    self.layout.setAlignment(player_vbox, Qt.AlignmentFlag.AlignVCenter)

    # Draw both canvases
    self.player_accu_canvas.draw()
    self.player_win_chance_canvas.draw()
    
def time_control_update(
        self: Self,
        index: str,
        dfs: dict[str, dd.DataFrame]) -> None:
    '''
    Info:
    Updates the user plot when a different time control is selected

    Parameters:
    - self (Self): The instance of the QMainWindow so we can directly access the needed plots
    - index: The index lookup for our selected time control 
    - dfs (dict[str, dd.DataFrame]): The dictionary of dask dataframes which contains our player data

    Returns:
    - None
    '''
    
    self.time_control = constants.TIME_CONTROLS[int(index)]
    self.player_accu_figure.clear()
    player_plots.create_player_accuracy_trend_plot(self.player_accu_canvas.figure.subplots(), dfs, self.start_year, self.end_year, self.time_control)
    self.player_accu_canvas.draw()
    
def update_player_plots(
        self: Self,
        start_year: int,
        end_year: int,
        dfs: dict[str, dd.DataFrame]) -> None:
    '''
    Info:
    Updates the user plot when a different time control is selected

    Parameters:
    - self (Self): The instance of the QMainWindow so we can directly access the needed plots
    - index: The index lookup for our selected time control 
    - dfs (dict[str, dd.DataFrame]): The dictionary of dask dataframes which contains our player data

    Returns:
    - None
    '''

    self.start_year = start_year
    self.end_year = end_year

    # Refresh both of the plots with the new start and end year
    self.player_accu_figure.clf()
    player_plots.create_player_accuracy_trend_plot(self.player_accu_canvas.figure.subplots(), dfs, self.start_year, self.end_year, self.time_control)
    self.player_accu_canvas.draw()

    self.player_win_chance_figure.clf()
    player_plots.create_player_elo_odds_plot(self.player_win_chance_canvas.figure.subplots(), dfs)
    self.player_win_chance_canvas.draw()

def update_year_range_label(
        self: Self) -> None:
    '''
    Info:
    Updates the year range label and repains the slider to be the correct range

    Parameters:
    - self (Self): The instance of the QMainWindow so we can directly access the year range label and range slider

    Returns:
    - None
    '''
    
    self.year_range_label.setText(f"Year range: {self.range_slider.start} - {self.range_slider.end}")
    self.range_slider.repaint()

def add_gm_widgets(
        self: Self,
        dfs: dict[str, dd.DataFrame]) -> None:
    '''
    Info:
    Creates the grandmaster widgets to display
        1) Titled Tuesday accuracy trend
        1) Glicko score trend over titeld tuesday games
        2) Grandmaster selection box

    Parameters:
    - self (Self): The instance of the QMainWindow so we can write the widgets directly to its main layout
    - dfs (dict[str, dd.DataFrame]): The dictionary of dask dataframes which contains our player data

    Returns:
    - None
    '''

    # Title
    label = QLabel("Titled Tuesday\n(2024 Late & Early)")
    label.setStyleSheet("""
        font-size: 55px;
        font-weight: bold;
        color: #81b64c;
        padding-top: 20px;
        padding-bottom: 20px;
    """)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.layout.addWidget(label, 1, 1, 1, 2)

    # Add graphs for titled tuesday and glicko trend 
    gm_graph_hbox = QHBoxLayout() 

    # (Left) Title tuesday accuracy
    tt_vbox = QVBoxLayout()
    label = QLabel("GM Titled Tuesday Accuracy")
    label.setStyleSheet("""
        font-size: 30px;
        font-weight: bold;
        color: #ebecd0;
        padding-top: 20px;
        padding-bottom: 20px;
    """)

    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.gm_tt_accu_fig = Figure()
    self.gm_tt_accu_fig.subplots_adjust(top=0.95)
    self.gm_tt_accu_fig.subplots_adjust(bottom=0.2)
    self.gm_tt_accu_canvas = FigureCanvas(self.gm_tt_accu_fig) # fig size in inches

    tt_vbox.addWidget(self.gm_tt_accu_canvas)
    tt_vbox.addWidget(label)
    gm_graph_hbox.addLayout(tt_vbox)
    gm_graph_hbox.addSpacing(30)

    # (Right) Glicko Trend
    gt_vbox = QVBoxLayout()
    label = QLabel("GM Glicko Trend")
    label.setStyleSheet("""
        font-size: 30px;
        font-weight: bold;
        color: #ebecd0;
        padding-top: 20px;
        padding-bottom: 20px;
    """)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter) 
    self.gm_glicko_trend_fig = Figure()
    self.gm_glicko_trend_fig.subplots_adjust(top=0.95)
    self.gm_glicko_trend_fig.subplots_adjust(bottom=0.2)
    self.gm_glicko_trend_canvas = FigureCanvas(self.gm_glicko_trend_fig) # fig size in inches
    gm_plots.create_grandmaster_plots(self.gm_tt_accu_canvas.figure.subplots(), self.gm_glicko_trend_canvas.figure.subplots(), dfs)

    gt_vbox.addWidget(self.gm_glicko_trend_canvas)
    gt_vbox.addWidget(label)
    gm_graph_hbox.addLayout(gt_vbox)

    self.layout.addLayout(gm_graph_hbox, 2, 1, 2, 2)
    
    # (Bottom) 
    self.tt_usernames = dfs[constants.TT]['username'].drop_duplicates().compute().tolist()
    tt_winners = dfs[constants.TT_W]
    tt_winner_counts = tt_winners['username'].value_counts() # value_counts gives descending order
    tt_winner_counts_dict=  dict(sorted(zip(tt_winner_counts.compute().index, tt_winner_counts.compute().values),  key=lambda item: item[1], reverse=True))
    self.tt_winners = [name for (name, win_count) in tt_winner_counts_dict.items()]

    gm_control_layout = QHBoxLayout()
    label = QLabel("Selected GM:")
    label.setStyleSheet("""
        font-size: 25px;
        font-weight: bold;
        color: #bdc4b4;
    """)
    gm_control_layout.addWidget(label)

    self.gm_control_box = QComboBox(self.main_widget)
    self.gm_control_box.addItems(self.tt_usernames)
    self.gm_control_box.setStyleSheet("""
        QComboBox {
            padding: 10px;
            margin: 5px;
            max-width: 300px; /* Prevent stretching */
            font-size: 25px;
            color: #81b64c
        }
    """)
    gm_control_layout.addWidget(self.gm_control_box)
    self.gm_control_box.currentIndexChanged.connect(lambda x: update_grandmaster_plots(self, x, dfs, call='box'))
    self.gm_control_box.setCurrentIndex(self.tt_usernames.index(self.gm))

    gm_control_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    container_widget = QWidget()
    container_widget.setLayout(gm_control_layout)
    self.layout.addWidget(container_widget, 4, 1, 1, 2, alignment=Qt.AlignmentFlag.AlignTop)

    self.gm_glicko_trend_canvas.draw()
    self.gm_tt_accu_canvas.draw()

def update_grandmaster_plots(
        self: Self,
        gm_index: int,
        dfs: dict[str, dd.DataFrame],
        call: str) -> None:
    '''
    Info:
    Updates grandmaster plots when the gm selection is changed to a different user

    Parameters:
    - self (Self): The instance of the QMainWindow so we can directly access the needed plots
    - gm_index: The index lookup for our GM name array, so we can select the chosen GM
    - dfs (dict[str, dd.DataFrame]): The dictionary of dask dataframes which contains our player data
    - call (str): Can either be 'list' or 'box', where:
        1) 'list' means the index was selected from the PlayerRankWidget list, which is tied to the tt_winners username list.
        2) 'box'  means the index was selected from the QComboBox list, which is tied to the tt_usernames username list.

    Returns:
    - None
    '''
    if call == 'list':
        self.gm = self.tt_winners[gm_index]
        gm_index = self.tt_usernames.index(self.gm)
    elif call == 'box':
        self.gm = self.tt_usernames[gm_index]
    
    # Refresh the accuracy plot
    self.gm_tt_accu_fig.clear()
    accu_ax = self.gm_tt_accu_canvas.figure.subplots()

    # Refresh the glicko plot
    self.gm_glicko_trend_fig.clear()
    glicko_ax = self.gm_glicko_trend_canvas.figure.subplots()

    gm_plots.create_grandmaster_plots(accu_ax, glicko_ax, dfs, self.gm)

    self.gm_tt_accu_canvas.draw()
    self.gm_glicko_trend_canvas.draw()

    self.gm_control_box.setCurrentIndex(gm_index)
    
def add_titled_tuesday_widgets(
        self: Self,
        dfs: dict[str, dd.DataFrame]) -> None:
    '''
    Info:
    Creates the titled tuesday widgets to display
        1) Interactive grand master ranking list
        2) The accuracy and glicko score plots

    Parameters:
    - self (Self): The instance of the QMainWindow so we can write the widgets directly to its main layout
    - dfs (dict[str, dd.DataFrame]): The dictionary of dask dataframes which contains our player data

    Returns:
    - None
    '''

    # MAIN HBOX (contains left player list and right plots, along with their titles)
    tt_layout = QHBoxLayout()

    ##########################
    # (LEFT VBOX) Top TT Players interactive feature: Click on name to switch gm widgets to focus on that player.
    ##########################

    list_vbox = QVBoxLayout()

    # Label
    label = QLabel("Player Rankings (by # of wins)")
    label.setStyleSheet("""
        font-size: 30px;
        font-weight: bold;
        color: #ebecd0;
        padding-top: 100px;
        padding-bottom: 20px;
    """)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # Player list
    tt_winners = dfs[constants.TT_W]
    tt_winner_counts = tt_winners['username'].value_counts() # value_counts gives descending order
    tt_winner_counts_dict=  dict(sorted(zip(tt_winner_counts.compute().index, tt_winner_counts.compute().values),  key=lambda item: item[1], reverse=True))
    tt_winners = [(rank + 1, name, win_count) for rank, (name, win_count) in enumerate(tt_winner_counts_dict.items()) ]
    player_list = PlayerRankWidget(tt_winners)
    player_list.player_selected.connect(lambda x: update_grandmaster_plots(self, x, dfs, call='list'))

    # Add the widgets
    list_vbox.addWidget(label)
    list_vbox.addWidget(player_list)

    tt_layout.addLayout(list_vbox)
    tt_layout.setAlignment(tt_layout, Qt.AlignmentFlag.AlignVCenter)

    ##########################
    # (RIGHT VBOX) # Player accuracy to otb accuracy and glicko score charts of the top players
    ##########################

    plots_vbox = QVBoxLayout() 

    # Title
    label = QLabel("Top 5 Player Trends")
    label.setStyleSheet("""
        font-size: 30px;
        font-weight: bold;
        color: #ebecd0;
        padding-top: 100px;
        padding-bottom: 20px;
    """)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    plots_vbox.addWidget(label)

    # Glicko plot
    self.tt_trends_fig = Figure()
    self.tt_trends_fig.subplots_adjust(top=0.8)
    self.tt_trends_fig.subplots_adjust(bottom=0.2)
    self.tt_trends_canvas = FigureCanvas(self.tt_trends_fig) # fig size in inches

    # Accuracy plot
    self.tt_trends_accu_fig = Figure()
    self.tt_trends_accu_fig.subplots_adjust(bottom=0.2)
    self.tt_trends_accu_canvas = FigureCanvas(self.tt_trends_accu_fig) # fig size in inches

    # Initiate the plots
    titled_tuesday_plots.create_titled_tuesday_trend_plots(
        self.tt_trends_canvas.figure.subplots(),
        self.tt_trends_accu_canvas.figure.subplots(),
        dfs
    )

    # Add the plots to the vbox
    plots_vbox.addWidget(self.tt_trends_canvas)
    plots_vbox.addWidget(self.tt_trends_accu_canvas)

    tt_layout.addLayout(plots_vbox)

    self.layout.addLayout(tt_layout, 5, 1, 2, 2)
    self.layout.setAlignment(tt_layout, Qt.AlignmentFlag.AlignTop)