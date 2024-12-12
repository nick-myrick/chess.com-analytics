import constants
import dask.dataframe as dd
import pandas as pd

def create_titled_tuesday_trend_plot(ax, dfs):
    
    tt_winners = dfs[constants.TT].loc[(dfs[constants.TT]["rank"] == 1) & (dfs[constants.TT]["round"] == 11)] # includes ties
    tt_winner_counts = tt_winners['username'].value_counts() # value_counts gives descending order
    tt_winner_counts_dict=  dict(sorted(zip(tt_winner_counts.compute().index, tt_winner_counts.compute().values),  key=lambda item: item[1], reverse=True))
    tt_winners = [(rank + 1, name, win_count) for rank, (name, win_count) in enumerate(tt_winner_counts_dict.items()) ]
    df = dfs[constants.TT]
    ax.tick_params(rotation=45, labelsize=10)

    full_date_range = pd.date_range(start='2022-07-01', end='2023-12-31', freq='MS')

    for (rank, gm_name, win_count) in tt_winners[0:5]:
        print(gm_name)
        df_new = df[df['username'] == gm_name]

        # Extract the date part using a regular expression
        df_new[['month', 'day', 'year']] = df_new['tournament'].str.extract(
            r'-(january|february|march|april|may|june|july|august|september|october|november|december)-(\d+)-(\d+)-'
        )
        df_new['month'] = df_new['month'].str.capitalize()

        # Convert to datetime using Dask
        df_new['datetime'] = dd.to_datetime(df_new[['year', 'month', 'day']].apply(lambda x: f"{x['year']}-{x['month']}-{x['day']}", axis=1, meta=('x', 'object')))

        df_new = df_new[(df_new['rating'].notnull()) & (df_new['rating'] != 0)]

        # Group by year and month and calculate the mean rating
        df_new['year_month'] = df_new['datetime'].dt.to_period('M')

        # Calculate mean ratings per month
        mean_values = df_new.groupby('year_month')['rating'].mean().compute()

        # Reindex to include all months in the full date range
        mean_values = mean_values.reindex(pd.period_range(start='2022-07', end='2023-12', freq='M'))
        mean_values.interpolate(method='linear', inplace=True)

        # Plot using the full date range
        ax.plot(mean_values.index.to_timestamp(), mean_values.values, label=gm_name)

    # Create the plot
    #ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.20), ncol=3)
    #ax.tick_params(rotation=45, labelsize=10)
    ax.set_xticks(full_date_range)
    ax.set_xticklabels([date.strftime('%m/%Y') for date in full_date_range], rotation=45, ha='right')
    ax.legend(loc='upper center', ncol=3, 
          bbox_to_anchor=(0.5, 1.00), frameon=False,
          handletextpad=0.4, columnspacing=0.1)
    ax.set_title('Average Ratings of TT Winners Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Average Glicko Rating')