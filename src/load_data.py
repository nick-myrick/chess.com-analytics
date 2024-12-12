import time
import dask.dataframe as dd
import constants

'''
Helper functions that load the necessary datasets and performs preprocessing
'''

def load(
        dfs: dict[str, dd.DataFrame]) -> dict[str, dd.DataFrame]:
    '''
    Info:
    Loads relevant dataframes 
    NOTE: USER GAMES ARE FULLY PREPROCESSED

    Parameters:
    - dfs (dict[str, dd.DataFrame]): The dataframe dictionary that we should store our dataframes to

    Returns:
    - dfs (dict[str, dd.DataFrame]): The dataframe with all of our datasets loaded to it
    '''
    dfs = {
        #"titled-tuesday": dd.read_csv(
        #    "hf://datasets/kirillgoltsman/titled-tuesday-chess-games/titled-tuesday.csv",
        #    dtype={"tournament": "string", "username": "string", "accuracy": "float64", "round": "int64", "rank": "int64", "rating": "int64"}
        #),
        "titled-tuesday": dd.read_csv(
            "processed-data/data-collection-tt/tt_games.csv",
            dtype={"tournament": "string", "username": "string", "accuracy": "float64", "round": "int64", "rank": "int64", "rating": "int64"}
        )
        #"2-million-user-games": dd.read_csv(
        #    "data\\user-games.csv",
        #    sep=';',
        #    dtype={'time_control': 'string'}
        #),
    }

    #dfs[USRGAMES] = dfs[USRGAMES].loc[(dfs[USRGAMES]['rating_white'] < 3999) & (dfs[USRGAMES]['rating_black'] < 4000)]

    dfs = pre_processing(dfs)

    return dfs

def pre_processing(
        dfs: dict[str, dd.DataFrame]) -> dict[str, dd.DataFrame]:
    '''
    Info:
    Performs necessary preprocessing to the datasets

    Parameters:
    - dfs (dict[str, dd.DataFrame]): The dataframe dictionary that we should preprocess

    Returns:
    - dfs (dict[str, dd.DataFrame]): The dataframe after performing preprocessing
    '''

    # Remove entries from earlier than 2024
    dfs[constants.TT][['month', 'day', 'year']] = dfs[constants.TT]['tournament'].str.extract(r'-(january|february|march|april|may|june|july|august|september|october|november|december)-(\d+)-(\d+)-')
    month_conversion = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
    }
    dfs[constants.TT]['year'] = dd.to_numeric(dfs[constants.TT]['year'], errors='coerce')
    dfs[constants.TT] = dfs[constants.TT][dfs[constants.TT]['year'] >= 2024].reset_index(drop=True)

    # Add 'date' datetime column for plotting
    dfs[constants.TT]['date'] = dd.to_datetime(
        dfs[constants.TT]['year'].astype(str) + "-" + dfs[constants.TT]['month'].str.lower().map(month_conversion).astype(str) + "-" + dfs[constants.TT]['day'].astype(str),
        format='%Y-%m-%d'
    )

    # Remove unecessary columns
    dfs[constants.TT] = dfs[constants.TT].drop(['month', 'day', 'year'], axis=1)

    # Filter null values from username and tournament id, as we'll need these for every type of plot/statistic
    dfs[constants.TT] = dfs[constants.TT].dropna(subset=['username', 'tournament'])
    dfs[constants.TT] = dfs[constants.TT].loc[(dfs[constants.TT]!=0).any(axis=1)]

    #dfs[constants.USRGAMES].dropna(subset=['white', 'end_date', 'white_elo'])
    #dfs[constants.USRGAMES].loc[(dfs[constants.USRGAMES]!=0).any(axis=1)]

    # Add date information
    df = dfs[constants.TT]
    tt_winners = df.loc[(df["rank"] == 1) & (df["round"] == 11)].drop_duplicates(subset=["date"]) # include all winners, drop games that are on the same day
    dfs[constants.TT_W] = tt_winners

    return dfs