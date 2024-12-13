from pathlib import Path
current_file = Path(__file__).resolve()

import constants

import dask.dataframe as dd
import pandas as pd
import matplotlib.axes

'''
Helper functions for add_widgets.py that creates all of the plots under General Player Statistics
'''

def create_player_accuracy_trend_plot(
        ax: matplotlib.axes.Axes,
        dfs: dict[str, dd.DataFrame],
        year_min: int,
        year_max: int,
        time_control='30 min') -> None:
    '''
    Info:
    Creates the player glicko accuracy trend plot on the given axes

    Parameters:
    - ax (Axes): The matplotlib axes that will be drawn to
    - dfs (dict[str, dd.DataFrame]): The dictionary of dask dataframes which contains our player data
    - year_min (int): The minimum year selected by our year range selection bar
    - year_max (int): The minimum year selected by our year range selection bar
    - time_control (str): The time control selected in our time control selection box.

    Returns:
    - None
    '''
    filepath = f"{constants.PROCESSED_DATA_PATH}\\player_data\\player-accu-{constants.TIME_CONTROLS_MAP[time_control]}"
    if not Path(filepath).is_file():
        # Get dataframe and filter by year range
        df = dfs[constants.USRGAMES]
        # Convert dates to datetime
        df['end_date'] = dd.to_datetime(df['end_date'])
        df = df[(df['time_control'] == constants.TIME_CONTROLS_MAP[time_control])]

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

    result['year_month'] = result['year'].astype(str) + "-" + result['month'].astype(str)  # Combine year and month
    x = result['year_month'] 
    y = result['white_elo'] 

    # Create the plot
    ax.scatter(x, y, marker='o', linestyle='-', label='Median Elo')

    # Customize the plot

    # Show only year labels on the x-axis
    ticks = range(0, len(result), 12)  # Show a tick every 12 months (1 year)
    ax.set_xticks(ticks)
    ax.set_xticklabels(result['year'].iloc[ticks], rotation=45, ha='right', fontsize=10)  # Show only the year as labels
    ax.legend()

def create_player_elo_odds_plot(
        ax: matplotlib.axes.Axes,
        dfs: dict[str, dd.DataFrame]) -> None:
    '''
    Info:
    Creates the player elo odds plot on the given axes

    Parameters:
    - ax (Axes): The matplotlib axes that will be drawn to
    - dfs (dict[str, dd.DataFrame]): The dictionary of dask dataframes which contains our player data

    Returns:
    - None
    '''
    output_csv = f"{constants.PROCESSED_DATA_PATH}\\player_data\\elo_win_percentages.csv"

    if not Path(output_csv).is_file():
        # Define ELO ranges in 100-point increments
        df = dfs[constants.USRGAMES]
        df = df.sample(frac=0.1, random_state=1) # Random sample to reduce compute time

        # Define ELO ranges in 100-point increments
        elo_ranges = [(i, i + 100) for i in range(0, 3000, 100)]

        results = []

        for lower_bound, upper_bound in elo_ranges:
            current_range_games = df[
                ((df['white_elo'] >= lower_bound) & (df['white_elo'] < upper_bound)) |
                ((df['black_elo'] >= lower_bound) & (df['black_elo'] < upper_bound))
            ]

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

            total_games = current_range_games[
                ((current_range_games['white_elo'] >= lower_bound) &
                 (current_range_games['white_elo'] < upper_bound) &
                 (current_range_games['white_elo'] >= current_range_games['black_elo'] + 100)) |
                ((current_range_games['black_elo'] >= lower_bound) &
                 (current_range_games['black_elo'] < upper_bound) &
                 (current_range_games['black_elo'] >= current_range_games['white_elo'] + 100))
            ].shape[0].compute()

            win_percentage = (wins / total_games * 100) if total_games > 0 else None

            if win_percentage is not None:
                results.append({'ELO Range': f'{lower_bound}-{upper_bound}', 'Win Percentage vs Lower': win_percentage})
            print("1 iteration completed")

        # Save results to CSV
        result_df = dd.from_pandas(pd.DataFrame(results), npartitions=1)
        result_df.to_csv(output_csv, single_file=True, index=False)

    result_df = dd.read_csv(output_csv).compute()
    x = result_df['ELO Range']
    y = result_df['Win Percentage vs Lower']
    line, = ax.plot(x, y, marker='o', linestyle='-')
    ax.set_xticks(x)
    ax.set_xticklabels(x, rotation=45, ha='right', fontsize=10)
    ax.set_ylim([0, 100])
    ax.set_xlabel('Elo range')
    ax.set_ylabel('Win chance (%)')

    annot = ax.annotate(
        "", xy=(0,0), xytext=(0,-25),
        textcoords="offset points", va="top",
        ha="center",
        bbox=dict(
            boxstyle="round", fc='white',
            ec='black', alpha=1.0,
            pad=0.5
        ),
        arrowprops=dict(arrowstyle="->")
    )
    annot.set_visible(False)
    
    def update_annot(ind):
        x, y = line.get_data()
        annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
        text = f"Your Glicko Range: [{x[ind["ind"][0]]}]\n\nEstimated win chance vs. Glicko 100 points lower:\n{y[ind['ind'][0]]:.2f}%"
        annot.set_text(text)
        
        annot.xytext = (0, -25)
        annot.set_va("top")
        annot.set_ha("center")

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = line.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                ax.figure.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    ax.figure.canvas.draw_idle()

    ax.figure.canvas.mpl_connect("motion_notify_event", hover)