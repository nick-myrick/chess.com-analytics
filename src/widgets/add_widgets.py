# Custom imports
import plotting.player_plots as player_plots
import plotting.gm_plots as gm_plots
import plotting.titled_tuesday_plots as titled_tuesday_plots
import constants

# Plotting
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure

# UI
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QLabel, QWidget, QHBoxLayout, QVBoxLayout
# Custom UI
from widgets.QRangeSlider import *
from widgets.PlayerRankWidget import *

def add_player_widgets(self, dfs):
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
        font-size: 40px;
        font-weight: bold;
        color: #81b64c;
        padding-top: 20px;
        padding-bottom: 20px;
    """)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.layout.addWidget(label, 1, 0)

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
    self.layout.addWidget(label, 2, 0)
    self.player_accu_figure = Figure()
    self.player_accu_figure.subplots_adjust(bottom=0.2)
    self.player_accu_canvas = FigureCanvas(self.player_accu_figure) # fig size in inches
    player_plots.create_player_accuracy_trend_plot(self.player_accu_canvas.figure.subplots(), dfs, self.start_year, self.end_year, self.time_control)
    self.layout.addWidget(self.player_accu_canvas, 3, 0)

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

    #year_range_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    time_control_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    containerLayout = QHBoxLayout()
    containerLayout.addLayout(time_control_layout)
    containerLayout.addLayout(year_range_layout)
    containerLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.layout.addLayout(containerLayout, 4, 0)

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
    self.layout.addWidget(label, 5, 0)
    self.player_win_chance_figure = Figure()
    self.player_win_chance_figure.subplots_adjust(bottom=0.2)
    self.player_win_chance_canvas = FigureCanvas(self.player_win_chance_figure) # fig size in inches
    player_plots.create_player_elo_odds_plot(self.player_win_chance_canvas.figure.subplots(), dfs, self.start_year, self.end_year)
    self.layout.addWidget(self.player_win_chance_canvas, 6, 0)


    # Draw both canvases
    self.player_accu_canvas.draw()
    self.player_win_chance_canvas.draw()
    
def time_control_update(self, index, dfs):
    self.time_control = constants.TIME_CONTROLS[int(index)]
    self.player_accu_figure.clear()
    player_plots.create_player_accuracy_trend_plot(self.player_accu_canvas.figure.subplots(), dfs, self.start_year, self.end_year, self.time_control)
    self.player_accu_canvas.draw()
    
def update_player_plots(self, start_year, end_year, dfs):
    self.start_year = start_year
    self.end_year = end_year
    # Refresh both of the plots with the new start and end year
    self.player_accu_figure.clf()
    player_plots.create_player_accuracy_trend_plot(self.player_accu_canvas.figure.subplots(), dfs, self.start_year, self.end_year, self.time_control)
    self.player_accu_canvas.draw()

    self.player_win_chance_figure.clf()
    player_plots.create_player_elo_odds_plot(self.player_win_chance_canvas.figure.subplots(), dfs, self.start_year, self.end_year)
    self.player_win_chance_canvas.draw()

def update_year_range_label(self):
    self.year_range_label.setText(f"Year range: {self.range_slider.start} - {self.range_slider.end}")
    self.range_slider.repaint()

def add_gm_widgets(self, dfs):
    '''
    Two columns, 3 Rows. Top right of screen.
    '''
    # Title
    label = QLabel("Grandmaster Statistics")
    label.setStyleSheet("""
        font-size: 40px;
        font-weight: bold;
        color: #81b64c;
        padding-top: 20px;
        padding-bottom: 20px;
    """)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.layout.addWidget(label, 1, 1, 1, 2)

    # Add graphs for titled tuesday and glicko trend 
    gm_graph_layout = QHBoxLayout() # Hoz. container

    # (Left) Title tuesday accuracy

    tt_vbox = QVBoxLayout() # Vertical container
    label = QLabel("Titled Tuesday Accuracy")
    label.setStyleSheet("""
        font-size: 30px;
        font-weight: bold;
        color: #ebecd0;
        padding-top: 20px;
        padding-bottom: 20px;
    """)

    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.gm_tt_accu_fig = Figure()
    self.gm_tt_accu_fig.subplots_adjust(bottom=0.2)
    self.gm_tt_accu_canvas = FigureCanvas(self.gm_tt_accu_fig) # fig size in inches
    gm_plots.create_grandmaster_tt_accu_plot(self.gm_tt_accu_canvas.figure.subplots(), dfs)

    tt_vbox.addWidget(self.gm_tt_accu_canvas)
    tt_vbox.addWidget(label)
    gm_graph_layout.addLayout(tt_vbox)
    gm_graph_layout.addSpacing(30)

    # (Right) Glicko Trend
    gt_vbox = QVBoxLayout() # Vertical container
    label = QLabel("Glicko Trend")
    label.setStyleSheet("""
        font-size: 30px;
        font-weight: bold;
        color: #ebecd0;
        padding-top: 20px;
        padding-bottom: 20px;
    """)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter) 
    self.gm_glicko_trend_fig = Figure()
    self.gm_glicko_trend_fig.subplots_adjust(bottom=0.2)
    self.gm_glicko_trend_canvas = FigureCanvas(self.gm_glicko_trend_fig) # fig size in inches
    gm_plots.create_grandmaster_trend_plot(self.gm_glicko_trend_canvas.figure.subplots(), dfs)

    gt_vbox.addWidget(self.gm_glicko_trend_canvas)
    gt_vbox.addWidget(label)
    gm_graph_layout.addLayout(gt_vbox)

    self.layout.addLayout(gm_graph_layout, 2, 1, 2, 2)
    
    # (Bottom) 
    tt_winners = dfs[constants.TT].loc[(dfs[constants.TT]["rank"] == 1) & (dfs[constants.TT]["round"] == 11)] # includes ties
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
    self.gm_control_box.addItems(self.tt_winners)
    self.gm_control_box.setStyleSheet("""
        QComboBox {
            padding: 10px;
            margin: 5px;
            max-width: 200px; /* Prevent stretching */
            font-size: 25px;
        }
    """)
    gm_control_layout.addWidget(self.gm_control_box)
    self.gm_control_box.currentIndexChanged.connect(lambda x: update_grandmaster_plots(self, x, dfs))
    self.gm_control_box.setCurrentIndex(self.tt_winners.index(self.gm))


    gm_control_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    container_widget = QWidget()
    container_widget.setLayout(gm_control_layout)
    self.layout.addWidget(container_widget, 4, 1, 1, 2, alignment=Qt.AlignmentFlag.AlignTop)

    self.gm_glicko_trend_canvas.draw()
    self.gm_tt_accu_canvas.draw()

def update_grandmaster_plots(self, gm_index, dfs):
    gm_name = self.tt_winners[gm_index]
    self.gm_tt_accu_fig.clear()
    ax = self.gm_tt_accu_canvas.figure.subplots()
    gm_plots.create_grandmaster_tt_accu_plot(ax, dfs, gm_name)
    self.gm_tt_accu_canvas.draw()

    self.gm_glicko_trend_fig.clear()
    ax = self.gm_glicko_trend_canvas.figure.subplots()
    gm_plots.create_grandmaster_trend_plot(ax, dfs, gm_name)
    self.gm_glicko_trend_canvas.draw()

    self.gm_control_box.setCurrentIndex(gm_index)
    
def add_titled_tuesday_widgets(self, dfs):
    '''
    Two columns, 3 Rows. Bottom right of screen.
    '''

    # Title
    label = QLabel("Titled Tuesday (7/2022-12/2023)")
    label.setStyleSheet("""
        font-size: 40px;
        font-weight: bold;
        color: #81b64c;
        padding-top: 40px;
        padding-bottom: 20px;
    """)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.layout.addWidget(label, 5, 1, 1, 2)

    tt_layout = QHBoxLayout() # Hoz. container
    # (Left) Top TT Players OPTIONAL FEATURE: Click on name to switch gm widgets to focus on that player.
    tt_top_vbox = QVBoxLayout() # Vertical container

    label = QLabel("Best Players")
    label.setStyleSheet("""
        font-size: 30px;
        font-weight: bold;
        color: #ebecd0;
        padding-top: 20px;
        padding-bottom: 20px;
    """)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    tt_top_vbox.addWidget(label)

    tt_winners = dfs[constants.TT].loc[(dfs[constants.TT]["rank"] == 1) & (dfs[constants.TT]["round"] == 11)] # includes ties
    tt_winner_counts = tt_winners['username'].value_counts() # value_counts gives descending order
    tt_winner_counts_dict=  dict(sorted(zip(tt_winner_counts.compute().index, tt_winner_counts.compute().values),  key=lambda item: item[1], reverse=True))
    tt_winners = [(rank + 1, name, win_count) for rank, (name, win_count) in enumerate(tt_winner_counts_dict.items()) ]

    player_list = PlayerRankWidget(tt_winners)
    tt_top_vbox.addWidget(player_list)
    tt_layout.addLayout(tt_top_vbox)

    # (Right) # Player accuracy to otb accuracy chart of the top players
    tt_trends_vbox = QVBoxLayout() # Vertical container

    label = QLabel("Top 5 Player Glicko Trends")
    label.setStyleSheet("""
        font-size: 30px;
        font-weight: bold;
        color: #ebecd0;
        padding-top: 100px;
        padding-bottom: 20px;
    """)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    tt_trends_vbox.addWidget(label)

    self.tt_trends_fig = Figure()
    self.tt_trends_fig.subplots_adjust(bottom=0.2)
    self.tt_trends_canvas = FigureCanvas(self.tt_trends_fig) # fig size in inches
    titled_tuesday_plots.create_titled_tuesday_trend_plot(self.tt_trends_canvas.figure.subplots(), dfs)
    tt_trends_vbox.addWidget(self.tt_trends_canvas)

    tt_layout.addLayout(tt_trends_vbox)
    player_list.player_selected.connect(lambda x: update_grandmaster_plots(self, x, dfs))


    self.layout.addLayout(tt_layout, 6, 1, 2, 2)
    tt_layout.setStretch(0, 1)
    tt_layout.setStretch(1, 1)

    self.tt_trends_canvas.draw()