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
        "titled-tuesday": dd.read_csv(
            "hf://datasets/kirillgoltsman/titled-tuesday-chess-games/titled-tuesday.csv",
            dtype={"tournament": "string", "username": "string", "accuracy": "float64", "round": "int64", "rank": "int64", "rating": "int64"}
        ),
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
    dfs[constants.TT].dropna(subset=['username', 'tournament'])
    dfs[constants.TT].loc[(dfs[constants.TT]!=0).any(axis=1)]

    #dfs[constants.USRGAMES].dropna(subset=['white', 'end_date', 'white_elo'])
    #dfs[constants.USRGAMES].loc[(dfs[constants.USRGAMES]!=0).any(axis=1)]

    df = dfs[constants.TT]
    df[['month', 'day', 'year']] = df['tournament'].str.extract(r'-(january|february|march|april|may|june|july|august|september|october|november|december)-(\d+)-(\d+)-')
    df['month'] = df['month'].str.capitalize()
    df['datetime'] = dd.to_datetime(df[['month', 'day', 'year']].apply(lambda x: f"{x['month']} {x['day']} {x['year']}", axis=1))

    tt_winners = df.loc[(df["rank"] == 1) & (df["round"] == 11)].drop_duplicates(subset=["datetime"]) # include all winners, drop games that are on the same day
    dfs[constants.TT_W] = tt_winners

    return dfs