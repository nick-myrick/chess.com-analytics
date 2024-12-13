import constants
import pandas as pd
import dask.dataframe as dd
import matplotlib.axes
import matplotlib.dates as mdates

'''
Helper functions for add_widgets.py that creates all of the plots under Grandmaster
TODO: these could be combined into one function
'''

def create_grandmaster_tt_accu_plot(
        ax: matplotlib.axes.Axes,
        dfs: dict[str, dd.DataFrame],
        gm_name='hikaru') -> None:
    '''
    Info:
    Creates the grandmaster titled tuesday accuracy trend plot on the given axes

    Parameters:
    - ax (Axes): The matplotlib axes that will be drawn to
    - dfs (dict[str, dd.DataFrame]): The dictionary of dask dataframes which contains our player data
    - gm_name (str): The username of the gm whose info we wish to display

    Returns:
    - None
    '''

    # Filter by gm username
    df = dfs[constants.TT]
    df = df[df['username'] == gm_name]
    df = df[(df['accuracy'].notnull()) & (df['accuracy'] != 0)]

    # Scatter plot
    ax.scatter(df['date'].compute(), df['accuracy'].compute(), s=5)

    # Calculate and plot mean accuracy per day
    mean_values = df.groupby('date')['accuracy'].mean().reset_index()
    ax.plot(mean_values['date'].compute(), mean_values['accuracy'].compute(), color='red', linewidth=2, label='Mean Accuracy')
    
    ax.set_ylabel("(%)")
    ax.legend(loc='upper left')
    ax.tick_params(axis='x', labelrotation=45, labelsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)

def create_grandmaster_trend_plot(
        ax: matplotlib.axes.Axes,
        dfs: dict[str, dd.DataFrame],
        gm_name='hikaru') -> None:
    '''
    Info:
    Creates the grandmaster titled tuesday accuracy trend plot on the given axes

    Parameters:
    - ax (Axes): The matplotlib axes that will be drawn to
    - dfs (dict[str, dd.DataFrame]): The dictionary of dask dataframes which contains our player data
    - gm_name (str): The username of the gm whose info we wish to display

    Returns:
    - None
    '''

    # Filter by gm username
    df = dfs[constants.TT]
    df = df[df['username'] == gm_name]
    df = df[(df['accuracy'].notnull()) & (df['accuracy'] != 0)]

    # Scatter plot
    ax.scatter(df['date'].compute(), df['rating'].compute(), s=5)

    # Calculate and plot mean rating per day
    mean_values = df.groupby('date')['rating'].mean().reset_index()
    ax.plot(mean_values['date'].compute(), mean_values['rating'].compute(), color='red', linewidth=2, label='Mean Rating')
    
    ax.legend(loc='upper left')
    ax.tick_params(axis='x', labelrotation=45, labelsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)