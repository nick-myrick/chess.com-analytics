import constants
import pandas as pd
import dask.dataframe as dd
import matplotlib.axes
import matplotlib.dates as mdates

'''
Helper functions for add_widgets.py that creates all of the plots under Grandmaster
TODO: these could be combined into one function
'''

def create_grandmaster_plots(
        ax: matplotlib.axes.Axes,
        ax2: matplotlib.axes.Axes,
        dfs: dict[str, dd.DataFrame],
        gm_name='hikaru') -> None:
    '''
    Info:
    Creates the grandmaster titled tuesday accuracy trend plot on the given axes

    Parameters:
    - ax (Axes): The matplotlib axes that will be drawn to
    - dfs (dict[str, dd.DataFrame]): The dictionary of dask dataframes which contains our player data
    - type (str): "accu" or "glicko"
    - gm_name (str): The username of the gm whose info we wish to display

    Returns:
    - None
    '''

    # Filter by gm username
    df = dfs[constants.TT]
    df = df[(df['username'] == gm_name) & (df['accuracy'].notnull()) & (df['accuracy'] != 0)]

    selected_columns = ['date', 'accuracy', 'rating']
    df = df[selected_columns]

    df = df.compute()

    x = df['date']
    y = df['accuracy']
    y2 = df['rating']

    # Acscuracy plot
    ax.scatter(x, y, s=5)

    # Calculate and plot mean accuracy per day
    mean_accuracy = df.groupby('date')['accuracy'].mean().reset_index()

    x_line = mean_accuracy['date']

    ax.plot(x_line, mean_accuracy['accuracy'], color='red', linewidth=2, label='Mean Accuracy')
    
    ax.set_ylabel("(%)")
    ax.legend(loc='upper left')
    ax.tick_params(axis='x', labelrotation=45, labelsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)

    # Glicko plot
    ax2.scatter(x, y2, s=5)

    # Calculate and plot mean rating per day
    mean_rating = df.groupby('date')['rating'].mean().reset_index()
    ax2.plot(x_line, mean_rating['rating'], color='red', linewidth=2, label='Mean Rating')
    
    ax2.legend(loc='upper left')
    ax2.tick_params(axis='x', labelrotation=45, labelsize=10)
    ax2.grid(True, linestyle='--', alpha=0.6)