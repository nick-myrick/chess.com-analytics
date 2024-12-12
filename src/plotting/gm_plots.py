import constants
import dask.dataframe as dd

def create_grandmaster_tt_accu_plot(ax, dfs, gm_name='hikaru'):
    df = dfs[constants.TT]
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

def create_grandmaster_trend_plot(ax, dfs, gm_name='hikaru'):
    df = dfs[constants.TT]
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