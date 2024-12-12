import constants
import pandas as pd
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
    df = df[(df['rating'].notnull()) & (df['rating'] != 0)]

    df['year_month'] = df['year'].astype(str) + "-" + df['month'].astype(str)  # Combine year and month
    month_conversion = {
        "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, 
        "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
    }
    df['year_month_num'] = df['month'].map(month_conversion)

    df['year_month'] = df['month'].map(month_conversion).astype(str) + "/" + df['year'].astype(str)  # Combine year and month
    x = df['year_month']  # X-axis values
    y = df['accuracy']  # Y-axis values

    # Create the plot
    ax.scatter(x, y, s=5)
    #ticks = range(0, len(df), 12)  # Show a tick every 12 months (1 year)
    # Calculate mean accuracy per 'year_month'
    mean_values = df.groupby('year_month').agg({
        'accuracy': 'mean',
        'year_month_num': 'first',
        'year': 'first'
    }).reset_index()
    
    # Sort mean_values by year and month number to ensure chronological order
    mean_values = mean_values.sort_values(['year', 'year_month_num'])
    
    # Plot mean accuracy line
    ax.plot(mean_values['year_month'], mean_values['accuracy'], color='red', linewidth=2, label='Mean Accuracy')
    
    # Customize the plot
    ax.tick_params(rotation=45, labelsize=10)
    ax.set_xlabel("Date")
    ax.set_ylabel("Accuracy (%)")
    ax.legend(loc='upper left')
    ax.grid(True, linestyle='--', alpha=0.6)

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

    month_conversion = {
        "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, 
        "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
    }
    df['year_month_num'] = df['month'].map(month_conversion)
    df['year_month'] = df['month'].map(month_conversion).astype(str) + "/" + df['year'].astype(str)  # Combine year and month

    df = df[(df['rating'].notnull()) & (df['rating'] != 0)]
    x = df['year_month']  # X-axis values
    y = df['rating']  # Y-axis values

    # Create the plot
    ax.scatter(x, y, s=5)

    mean_values = df.groupby('year_month').agg({
        'rating': 'mean',
        'year_month_num': 'first',
        'year': 'first'
    }).reset_index()
    
    # Sort mean_values by year and month number to ensure chronological order
    mean_values = mean_values.sort_values(['year', 'year_month_num'])
    
    # Plot mean accuracy line
    ax.plot(mean_values['year_month'], mean_values['rating'], color='red', linewidth=2, label='Mean Rating')
    
    # Customize the plot
    ax.tick_params(rotation=45, labelsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_xlabel("Date")
    ax.set_ylabel("Glicko Rating")

    ax.legend(loc='upper left')