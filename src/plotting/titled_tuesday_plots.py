import constants
import dask.dataframe as dd
import pandas as pd
import matplotlib.dates as mdates
import matplotlib.axes

'''
Helper functions for add_widgets.py that creates all of the plots under Titled Tuesday
'''

def create_titled_tuesday_trend_plots(
        ax: matplotlib.axes.Axes,
        ax2: matplotlib.axes.Axes,
        dfs: dict[str, dd.DataFrame]) -> None:
    '''
    Info:
    Creates the titled tuesday accuracy and glicko trend plots on the given two axes

    Parameters:
    - ax (Axes): The matplotlib axes for the glicko score trend plot
    - ax2 (Axes): The matplotlib axes for the accuracy trend plot
    - dfs (dict[str, dd.DataFrame]): The dictionary of dask dataframes which contains our player data

    Returns:
    - None
    '''
    
    tt_winners = dfs[constants.TT_W]
    tt_winner_counts = tt_winners['username'].value_counts() # value_counts gives descending order
    tt_winner_counts_dict = dict(sorted(zip(tt_winner_counts.compute().index, tt_winner_counts.compute().values),  key=lambda item: item[1], reverse=True))
    tt_winners = [(rank + 1, name, win_count) for rank, (name, win_count) in enumerate(tt_winner_counts_dict.items()) ]

    ax.tick_params(rotation=45, labelsize=10)

    full_date_range = pd.date_range(start='2024-01-01', end='2024-12-31', freq='MS')

    lines_ax1 = []
    lines_ax2 = []

    for i, (rank, gm_name, win_count) in enumerate(tt_winners[0:5]):
        df = dfs[constants.TT]
        df = df[df['username'] == gm_name]
        df = df[(df['rating'].notnull()) & (df['rating'] != 0)]

        # Calculate mean ratings per month
        mean_values = df.groupby('date')['rating'].mean().reset_index()
        mean_accuracy = df.groupby('date')['accuracy'].mean().reset_index()

        # Reindex to include all months in the full date range
        line1, = ax.plot(mean_values['date'].compute(), mean_values['rating'].compute(), label=gm_name, marker='.')
        #line1, = ax.plot(mean_values.index.to_timestamp(), mean_values.values, label=gm_name, marker='.')
        #line2, = ax2.plot(mean_accuracy.index.to_timestamp(), mean_accuracy.values, marker='.')
        line2, = ax2.plot(mean_accuracy['date'].compute(), mean_accuracy['accuracy'].compute(), label=gm_name, marker='.')
        lines_ax1.append((line1, gm_name))
        lines_ax2.append((line2, f"{gm_name} Accuracy"))

    # Create the plot
    ax.set_title('Average Rating of TT Winners Over Time')
    ax.set_ylabel('Average Glicko Rating')
    ax.set_xticks(full_date_range)
    ax.set_xticklabels([date.strftime('%m/%Y') for date in full_date_range], rotation=45, ha='right')

    ax2.set_xticks(full_date_range)
    ax2.set_xticklabels([date.strftime('%m/%Y') for date in full_date_range], rotation=45, ha='right')
    ax.figure.legend(loc='upper center', ncol=3, 
        bbox_to_anchor=(0.5, 1.00), frameon=False,
        handletextpad=0.4, columnspacing=0.1
    )
    ax2.set_title('Average Accuracy of TT Winners Over Time')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Average Accuracy')

    # Add annotations on hover
    annot_ax = ax.annotate(
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
    annot_ax.set_visible(False)

    annot_ax2 = ax2.annotate(
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
    annot_ax2.set_visible(False)

    def update_annot(line, label, event, annot):
        x, y = line.get_data()

        x_numeric = mdates.date2num(x)

        idx = (abs(x_numeric - event.xdata)).argmin()
        annot.xy = (x[idx], y[idx])
        if event.canvas == ax.figure.canvas:
            text = f"{label}\nDate: {pd.Timestamp(x[idx]).strftime('%Y-%m')}\nGlicko Score: {y[idx]:.2f}"
        elif event.canvas == ax2.figure.canvas:
            text = f"{label}\nDate: {pd.Timestamp(x[idx]).strftime('%Y-%m')}\nAccuracy: {y[idx]:.2f}"
        annot.set_text(text)
        annot.get_bbox_patch().set_facecolor(line.get_color())
        annot.get_bbox_patch().set_alpha(0.8)

    def hover(event):
        hovered_ax = False
        hovered_ax2 = False

        if event.inaxes is None:
            annot_ax.set_visible(False)
            annot_ax2.set_visible(False)
            ax.figure.canvas.draw_idle()
            ax2.figure.canvas.draw_idle()
            return

        if event.canvas == ax.figure.canvas:
            for line, label in lines_ax1:
                if line.contains(event)[0]:
                    update_annot(line, label, event, annot_ax)
                    annot_ax.set_visible(True)
                    hovered_ax = True
            if not hovered_ax:
                annot_ax.set_visible(False)

        if event.canvas == ax2.figure.canvas:
            for line, label in lines_ax2:
                if line.contains(event)[0]:
                    update_annot(line, label, event, annot_ax2)
                    annot_ax2.set_visible(True)
                    hovered_ax2 = True
            if not hovered_ax2:
                annot_ax2.set_visible(False)

        ax.figure.canvas.draw_idle()
        ax2.figure.canvas.draw_idle()

    ax.figure.canvas.mpl_connect("motion_notify_event", hover)
    ax2.figure.canvas.mpl_connect("motion_notify_event", hover)
