import constants
import dask.dataframe as dd

def create_titled_tuesday_trend_plot(ax, dfs):
    
    tt_winners = dfs[constants.TT].loc[(dfs[constants.TT]["rank"] == 1) & (dfs[constants.TT]["round"] == 11)] # includes ties
    tt_winner_counts = tt_winners['username'].value_counts() # value_counts gives descending order
    tt_winner_counts_dict=  dict(sorted(zip(tt_winner_counts.compute().index, tt_winner_counts.compute().values),  key=lambda item: item[1], reverse=True))
    tt_winners = [(rank + 1, name, win_count) for rank, (name, win_count) in enumerate(tt_winner_counts_dict.items()) ]
    df = dfs[constants.TT]
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