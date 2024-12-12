import sys
import os
import time
from pathlib import Path
import numpy as np
import pandas as pd
import dask.dataframe as dd
import dask
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib as mpl
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QLabel, QWidget, QHBoxLayout, QVBoxLayout
from QRangeSlider import *
from PlayerRankWidget import *

TT = "titled-tuesday"
USRGAMES = "3-million-user-games"
GMLATEST = "gm-latest"
GMACCU = "gm-accuracy"
time_controls = ["1 min", "1|1", "2|1", "3 min", "3|2", "5 min", "10 min", "15|10", "30 min"] # There are a lot more.. these are the top ones
time_controls_map = {
    "1 min": "60",
    "1|1": "60+1",
    "2|1": "120+1",
    "3 min": "180",
    "3|2": "180+2",
    "5 min": "300",
    "10 min": "600",
    "15|10": "900+10",
    "30 min": "1800"
}

dfs = None

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        # Create starting layout
        super().__init__()

        self.setup_window()

        label = QLabel("Chess.com Statistics")
        label.setStyleSheet("""
            font-size: 45px;
            font-weight: bold;
            color: #ffffff;
            padding-top: 20px;
            padding-bottom: 20px;
            text-decoration: underline;
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(label, 0, 0, 1, 3)

        self.add_player_widgets()
        self.add_gm_widgets()
        self.add_titled_tuesday_widgets()
    
        self.player_accu_canvas.draw()
        self.player_win_chance_canvas.draw()
        self.gm_glicko_trend_canvas.draw()
        self.gm_tt_accu_canvas.draw()
    
    def setup_window(self):
        self.setWindowTitle("Chess.com Statistics")
        self.width = 1920
        self.height = 1920
        self.setGeometry(100, 100, self.width, self.height)
        self.setFixedSize(self.width, self.height)
        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QtWidgets.QGridLayout(self.main_widget)
        self.setStyleSheet("background-color: #2c2b29")

        self.layout.setHorizontalSpacing(100)  # Set space between columns 
        self.layout.setContentsMargins(20, 10, 20, 10)  # Left, Top, Right, Bottom (adjust as needed)


        self.layout.setColumnStretch(0, 2)  # Column 0 gets 1 part of the space
        self.layout.setColumnStretch(1, 3)
    
    def create_player_accuracy_trend_plot(self, ax, year_min, year_max, time_control='30 min'):
        filepath = f"save\\player-accu-{time_controls_map[time_control]}"
        if not Path(filepath).is_file():
            # Get dataframe and filter by year range
            df = dfs[USRGAMES]
            # Convert dates to datetime
            df['end_date'] = dd.to_datetime(df['end_date'])
            df = df[(df['time_control'] == time_controls_map[time_control])]

            # Extract year and month
            df['year'] = df['end_date'].dt.year
            df['month'] = df['end_date'].dt.month

            # Sort values within groups and remove duplicates
            df['group_key'] = df['year'].astype(str) + "-" + df['month'].astype(str)  # Create a group key for year and month
            df_sorted = df.sort_values(by=['group_key', 'white'])  # Sort within groups
            df = df_sorted.drop_duplicates(subset=['group_key', 'white'], keep='first')

            grouped_median = df.groupby(['year', 'month'])['white_elo'].median()

            # Compute the result (trigger Dask computation)
            result = grouped_median.compute()
            result = result.reset_index()  # Flatten the multi-index
            result.to_csv(filepath, index=False)
        else:
            result = dd.read_csv(filepath).compute()
        
        result = result.sort_values(by=['year', 'month'], ascending=True)
        result = result[(result['year'] >= year_min) & (result['year'] <= year_max)]

        #result = result.reset_index()  # Flatten the multi-index
        result['year_month'] = result['year'].astype(str) + "-" + result['month'].astype(str)  # Combine year and month
        x = result['year_month']  # X-axis values
        y = result['white_elo']  # Y-axis values

        # Create the plot
        ax.plot(x, y, marker='o', linestyle='-', label='Median Elo')

        # Customize the plot

        # Show only year labels on the x-axis
        ticks = range(0, len(result), 12)  # Show a tick every 12 months (1 year)
        ax.set_xticks(ticks)
        ax.set_xticklabels(result['year'].iloc[ticks], rotation=45, ha='right', fontsize=10)  # Show only the year as labels
        #ax.tick_params(axis='x', rotation=45, labelsize=10)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend()

    def create_player_elo_odds_plot(self, ax, year_min, year_max):
        output_csv = "save\\elo_win_percentages.csv"
        # Define ELO ranges in 100-point increments
        elo_ranges = [(i, i + 100) for i in range(0, 3000, 100)]
        df = dfs[USRGAMES]
        df = df.sample(frac=0.1, random_state=1)
        print("df sampled")

        if Path(output_csv).is_file():
            # Load the precomputed results
            result_df = dd.read_csv(output_csv).compute()
            x = result_df['ELO Range']
            y = result_df['Win Percentage vs Lower']
            ax.plot(x, y, marker='o', linestyle='-')
            ax.set_xticklabels(x, rotation=45, ha='right', fontsize=10)
            ax.set_ylim([0, 100])
            ax.set_xlabel('Elo range')
            ax.set_ylabel('Win chance (%)')
        else:
            # Define ELO ranges in 100-point increments
            elo_ranges = [(i, i + 100) for i in range(0, 3000, 100)]

            results = []

            for lower_bound, upper_bound in elo_ranges:
                # Filter games for players in the current ELO range
                current_range_games = df[
                    ((df['white_elo'] >= lower_bound) & (df['white_elo'] < upper_bound)) |
                    ((df['black_elo'] >= lower_bound) & (df['black_elo'] < upper_bound))
                ]

                # Count wins for higher-rated players within the range
                wins = current_range_games[
                    ((current_range_games['white_elo'] >= lower_bound) &
                     (current_range_games['white_elo'] < upper_bound) &
                     (current_range_games['white_elo'] >= current_range_games['black_elo'] + 100) &
                     (current_range_games['result'] == '1-0')) |
                    ((current_range_games['black_elo'] >= lower_bound) &
                     (current_range_games['black_elo'] < upper_bound) &
                     (current_range_games['black_elo'] >= current_range_games['white_elo'] + 100) &
                     (current_range_games['result'] == '0-1'))
                ].shape[0].compute()

                # Count total games within the range
                total_games = current_range_games[
                    ((current_range_games['white_elo'] >= lower_bound) &
                     (current_range_games['white_elo'] < upper_bound) &
                     (current_range_games['white_elo'] >= current_range_games['black_elo'] + 100)) |
                    ((current_range_games['black_elo'] >= lower_bound) &
                     (current_range_games['black_elo'] < upper_bound) &
                     (current_range_games['black_elo'] >= current_range_games['white_elo'] + 100))
                ].shape[0].compute()

                # Calculate win percentage
                win_percentage = (wins / total_games * 100) if total_games > 0 else None

                # Append results
                if win_percentage is not None:
                    results.append({'ELO Range': f'{lower_bound}-{upper_bound}', 'Win Percentage vs Lower': win_percentage})
                print("1 iteration completed")

            # Save results to CSV
            result_df = dd.from_pandas(pd.DataFrame(results), npartitions=1)
            result_df.to_csv(output_csv, single_file=True, index=False)
            print("Results saved to:", output_csv)
            print(result_df.compute())

    def create_grandmaster_tt_accu_plot(self, ax, gm_name='hikaru'):
        df = dfs[TT]
        print(gm_name)
        df = df[df['username'] == gm_name]
        # Extract the date part using a regular expression
        #df['date'] = df['tournament'].split("-")[4:6]
        
        df[['month', 'day', 'year']] = df['tournament'].str.extract(r'-(january|february|march|april|may|june|july|august|september|october|november|december)-(\d+)-(\d+)-')
        df['month'] = df['month'].str.capitalize()

        # Convert to datetime
        df['datetime'] = dd.to_datetime(df[['month', 'day', 'year']].apply(lambda x: f"{x['month']} {x['day']} {x['year']}", axis=1))

        # Sort the DataFrame by the datetime column
        df = df.sort_values('datetime', ascending=True).compute()
        print(df['datetime'])

        df['year_month'] = df['year'].astype(str) + "-" + df['month'].astype(str)  # Combine year and month
        x = df['year_month']  # X-axis values
        y = df['accuracy']  # Y-axis values

        # Create the plot
        ax.scatter(x, y, s=5)
        #ticks = range(0, len(df), 12)  # Show a tick every 12 months (1 year)
        #ax.set_xticks(ticks)
        #ax.set_xticklabels(df['year'].iloc[ticks], rotation=45, ha='right', fontsize=10)  # Show only the year as labels
        ax.tick_params(rotation=45, labelsize=10)
        #ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend()

    def create_grandmaster_trend_plot(self, ax, gm_name='hikaru'):
        df = dfs[TT]
        print(gm_name)
        df = df[df['username'] == gm_name]
        # Extract the date part using a regular expression
        #df['date'] = df['tournament'].split("-")[4:6]
        
        df[['month', 'day', 'year']] = df['tournament'].str.extract(r'-(january|february|march|april|may|june|july|august|september|october|november|december)-(\d+)-(\d+)-')
        df['month'] = df['month'].str.capitalize()

        # Convert to datetime
        df['datetime'] = dd.to_datetime(df[['month', 'day', 'year']].apply(lambda x: f"{x['month']} {x['day']} {x['year']}", axis=1))

        # Sort the DataFrame by the datetime column
        df = df.sort_values('datetime', ascending=True).compute()
        print(df['datetime'])

        df['year_month'] = df['year'].astype(str) + "-" + df['month'].astype(str)  # Combine year and month
        x = df['year_month']  # X-axis values
        y = df['rating']  # Y-axis values

        # Create the plot
        ax.scatter(x, y, s=5)
        #ticks = range(0, len(df), 12)  # Show a tick every 12 months (1 year)
        #ax.set_xticks(ticks)
        #ax.set_xticklabels(df['year'].iloc[ticks], rotation=45, ha='right', fontsize=10)  # Show only the year as labels
        ax.tick_params(rotation=45, labelsize=10)
        #ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend()

    def create_titled_tuesday_trend_plot(self, ax):
        
        tt_winners = dfs[TT].loc[(dfs[TT]["rank"] == 1) & (dfs[TT]["round"] == 11)] # includes ties
        tt_winner_counts = tt_winners['username'].value_counts() # value_counts gives descending order
        tt_winner_counts_dict=  dict(sorted(zip(tt_winner_counts.compute().index, tt_winner_counts.compute().values),  key=lambda item: item[1], reverse=True))
        tt_winners = [(rank + 1, name, win_count) for rank, (name, win_count) in enumerate(tt_winner_counts_dict.items()) ]
        df = dfs[TT]
        ax.tick_params(rotation=45, labelsize=10)

        for (rank, gm_name, win_count) in tt_winners[0:5]:
            print(gm_name)
            df_new = df[df['username'] == gm_name]

            # Extract the date part using a regular expression
            df_new[['month', 'day', 'year']] = df_new['tournament'].str.extract(
                r'-(january|february|march|april|may|june|july|august|september|october|november|december)-(\d+)-(\d+)-'
            )
            df_new['month'] = df_new['month'].str.capitalize()

            # Convert to datetime
            df_new['datetime'] = dd.to_datetime(
                df_new[['month', 'day', 'year']].apply(lambda x: f"{x['month']} {x['day']} {x['year']}", axis=1)
            )

            # Sort by datetime
            df_new = df_new.sort_values('datetime', ascending=True).compute()

            # Create year_month column for grouping
            df_new['year_month'] = df_new['year'].astype(str) + "-" + df_new['month'].astype(str)  # Combine year and month
            #df_new['year_month'] = df_new['datetime'].dt.to_period('M')

            # Group by year_month and calculate the median rating
            mean_values = df_new.groupby('year_month')['rating'].median()

            # Ensure X-axis is sorted correctly
            #mean_values = mean_values.sort_index()
            x = df_new['year_month'].drop_duplicates()
            print("X:")
            print(x)

            # Plot using sorted X (mean_values.index) and Y (mean_values.values)
            ax.scatter(x, mean_values, label=gm_name)

        # Create the plot
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.20), ncol=3)
        ax.tick_params(rotation=45, labelsize=10)


    
    def add_player_widgets(self):
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
            font-size: 30px;
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
            font-size: 25px;
            font-weight: bold;
            color: #ebecd0;
            padding-top: 20px;
            padding-bottom: 20px;
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(label, 2, 0)
        self.player_accu_figure = Figure()
        self.player_accu_canvas = FigureCanvas(self.player_accu_figure) # fig size in inches
        self.create_player_accuracy_trend_plot(self.player_accu_canvas.figure.subplots(), self.start_year, self.end_year, self.time_control)
        self.layout.addWidget(self.player_accu_canvas, 3, 0)

        # Time Control Selection
        time_control_layout = QHBoxLayout()
        label = QLabel("Time Control:")
        label.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            color: #bdc4b4;
        """)
        time_control_layout.addWidget(label)

        self.time_control_box = QComboBox(self.main_widget)
        self.time_control_box.addItems(time_controls)
        self.time_control_box.setStyleSheet("""
            QComboBox {
                padding: 10px;
                margin: 5px;
                max-width: 200px; /* Prevent stretching */
                font-size: 15px;
            }
        """)
        time_control_layout.addWidget(self.time_control_box)
        self.time_control_box.currentIndexChanged.connect(self.time_control_update)
        self.time_control_box.setCurrentIndex(time_controls.index(self.time_control))


        time_control_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container_widget = QWidget()
        container_widget.setLayout(time_control_layout)
        self.layout.addWidget(container_widget, 4, 0)

        # Winning chances canvas
        label = QLabel("Winning Odds Against Lower Brackets")
        label.setStyleSheet("""
            font-size: 25px;
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
        self.create_player_elo_odds_plot(self.player_win_chance_canvas.figure.subplots(), self.start_year, self.end_year)
        self.layout.addWidget(self.player_win_chance_canvas, 6, 0)

        # Year range selection
        self.year_range_label = QLabel(f"Year range: {self.start_year} - {self.end_year}")
        self.year_range_label.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            color: #bdc4b4;
            padding-top: 200px;
        """)
        self.year_range_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.year_range_label, 7, 0)

        self.range_slider = QRangeSlider(self.start_year, self.end_year)
        self.layout.addWidget(self.range_slider, 8, 0)
        self.range_slider.rangeChanged.connect(self.update_player_plots)

        self.range_slider.update = self.update_year_range_label
    
    def time_control_update(self, index):
        self.time_control = time_controls[int(index)]
        self.player_accu_figure.clear()
        ax = self.player_accu_canvas.figure.subplots()
        self.create_player_accuracy_trend_plot(ax, self.start_year, self.end_year, self.time_control)
        self.player_accu_canvas.draw()
    
    def update_player_plots(self, start_year, end_year):
        self.start_year = start_year
        self.end_year = end_year
        # Refresh both of the plots with the new start and end year
        self.player_accu_figure.clear()
        ax = self.player_accu_canvas.figure.subplots()
        self.create_player_accuracy_trend_plot(ax, start_year, end_year, self.time_control)
        self.player_accu_canvas.draw()

        self.player_win_chance_figure.clear()
        ax = self.player_win_chance_canvas.figure.subplots()
        self.create_player_elo_odds_plot(ax, start_year, end_year)
        self.player_win_chance_canvas.draw()

    def update_year_range_label(self):
        self.year_range_label.setText(f"Year range: {self.range_slider.start} - {self.range_slider.end}")
        self.range_slider.repaint()

    def add_gm_widgets(self):
        '''
        Two columns, 3 Rows. Top right of screen.
        '''
        # Title
        label = QLabel("Grandmaster Statistics")
        label.setStyleSheet("""
            font-size: 30px;
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
            font-size: 25px;
            font-weight: bold;
            color: #ebecd0;
            padding-top: 20px;
            padding-bottom: 20px;
        """)

        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gm_tt_accu_fig = Figure()
        self.gm_tt_accu_fig.subplots_adjust(bottom=0.3)
        self.gm_tt_accu_canvas = FigureCanvas(self.gm_tt_accu_fig) # fig size in inches
        self.create_grandmaster_tt_accu_plot(self.gm_tt_accu_canvas.figure.subplots())

        tt_vbox.addWidget(self.gm_tt_accu_canvas)
        tt_vbox.addWidget(label)
        gm_graph_layout.addLayout(tt_vbox)
        gm_graph_layout.addSpacing(30)

        # (Right) Glicko Trend
        gt_vbox = QVBoxLayout() # Vertical container
        label = QLabel("Glicko Trend")
        label.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            color: #ebecd0;
            padding-top: 20px;
            padding-bottom: 20px;
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.gm_glicko_trend_fig = Figure()
        self.gm_glicko_trend_fig.subplots_adjust(bottom=0.3)
        self.gm_glicko_trend_canvas = FigureCanvas(self.gm_glicko_trend_fig) # fig size in inches
        self.create_grandmaster_trend_plot(self.gm_glicko_trend_canvas.figure.subplots())

        gt_vbox.addWidget(self.gm_glicko_trend_canvas)
        gt_vbox.addWidget(label)
        gm_graph_layout.addLayout(gt_vbox)

        self.layout.addLayout(gm_graph_layout, 2, 1, 2, 2)
        
        # (Bottom) 
        tt_winners = dfs[TT].loc[(dfs[TT]["rank"] == 1) & (dfs[TT]["round"] == 11)] # includes ties
        tt_winner_counts = tt_winners['username'].value_counts() # value_counts gives descending order
        tt_winner_counts_dict=  dict(sorted(zip(tt_winner_counts.compute().index, tt_winner_counts.compute().values),  key=lambda item: item[1], reverse=True))
        self.tt_winners = [name for (name, win_count) in tt_winner_counts_dict.items()]

        gm_control_layout = QHBoxLayout()
        label = QLabel("Selected GM:")
        label.setStyleSheet("""
            font-size: 15px;
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
                font-size: 15px;
            }
        """)
        gm_control_layout.addWidget(self.gm_control_box)
        self.gm_control_box.currentIndexChanged.connect(self.update_grandmaster_plots)
        self.gm_control_box.setCurrentIndex(self.tt_winners.index(self.gm))


        gm_control_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container_widget = QWidget()
        container_widget.setLayout(gm_control_layout)
        self.layout.addWidget(container_widget, 4, 1, 1, 2, alignment=Qt.AlignmentFlag.AlignTop)


    
    def update_grandmaster_plots(self, gm_index):
        gm_name = self.tt_winners[gm_index]
        self.gm_tt_accu_fig.clear()
        ax = self.gm_tt_accu_canvas.figure.subplots()
        self.create_grandmaster_tt_accu_plot(ax, gm_name)
        self.gm_tt_accu_canvas.draw()

        self.gm_glicko_trend_fig.clear()
        ax = self.gm_glicko_trend_canvas.figure.subplots()
        self.create_grandmaster_trend_plot(ax, gm_name)
        self.gm_glicko_trend_canvas.draw()

        self.gm_control_box.setCurrentIndex(gm_index)
    
    def add_titled_tuesday_widgets(self):
        '''
        Two columns, 3 Rows. Bottom right of screen.
        '''

        # Title
        label = QLabel("Titled Tuesday (Jul2022-Dec2023)")
        label.setStyleSheet("""
            font-size: 30px;
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
            font-size: 25px;
            font-weight: bold;
            color: #ebecd0;
            padding-top: 20px;
            padding-bottom: 20px;
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tt_top_vbox.addWidget(label)

        tt_winners = dfs[TT].loc[(dfs[TT]["rank"] == 1) & (dfs[TT]["round"] == 11)] # includes ties
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
            font-size: 25px;
            font-weight: bold;
            color: #ebecd0;
            padding-top: 100px;
            padding-bottom: 20px;
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tt_trends_vbox.addWidget(label)

        self.tt_trends_fig = Figure()
        self.tt_trends_fig.subplots_adjust(bottom=0.3)
        self.tt_trends_canvas = FigureCanvas(self.tt_trends_fig) # fig size in inches
        self.create_titled_tuesday_trend_plot(self.tt_trends_canvas.figure.subplots())
        tt_trends_vbox.addWidget(self.tt_trends_canvas)

        tt_layout.addLayout(tt_trends_vbox)
        player_list.player_selected.connect(self.update_grandmaster_plots)


        self.layout.addLayout(tt_layout, 6, 1, 2, 2)
        tt_layout.setStretch(0, 1)
        tt_layout.setStretch(1, 1)

def main():
    # Load dataframes and start that shiit
    print("Loading dataframes")
    start = time.time()
    global dfs
    dfs = {
        "titled-tuesday": dd.read_csv(
            "hf://datasets/kirillgoltsman/titled-tuesday-chess-games/titled-tuesday.csv",
            dtype={"tournament": "string"}
        ),
        #"3-million-user-games": dd.read_parquet(
        #    "data\\3-million-games.parquet"
        #),
        "3-million-user-games": dd.read_csv(
            "data\\user-games.csv",
            sep=';',
            dtype={'time_control': 'string'}
        ),
        "gm-latest": dd.read_csv(
            "data\\gm-games-latest.csv",
            usecols=[
                'Date','White','Black','BlackElo','WhiteElo'
            ]
        ), # Up to 2024
        "gm-accuracy": dd.read_csv(
            "data\\gm-games-accuracy.csv",
            usecols=[
                'player','player_name','white_Accuracy','black_Accuracy','Date','WhiteElo','BlackElo'
            ]
        ) # Only up to 2022, note: most games don't have accuracy?
    }
    end = time.time()
    length = end - start
    print(f"Time to load dataframes: {length}")

    # TODO: Fix dropna to only drop certain features
    dfs[TT].dropna(subset=['username', 'accuracy', 'rating', 'rank', 'tournament'])
    #dfs[USRGAMES].dropna(subset=['rating_white', 'rating_black', 'date'])
    dfs[USRGAMES].dropna(subset=['white', 'end_date', 'white_elo'])
    dfs[GMLATEST].dropna(subset=['WhiteElo', 'BlackElo', 'White', 'Black'])
    dfs[GMACCU].dropna(subset=['WhiteElo', 'BlackElo', 'player_name'])

    #dfs[USRGAMES] = dfs[USRGAMES].loc[(dfs[USRGAMES]['rating_white'] < 4000) & (dfs[USRGAMES]['rating_black'] < 4000)]

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