import time
import dask.dataframe as dd
import constants

def load(dfs):
    '''
    Loads relevant dataframes 
    NOTE: USER GAMES ARE FULLY PREPROCESSED
    '''
    print("Loading dataframes")
    start = time.time()
    dfs = {
        "titled-tuesday": dd.read_csv(
            "hf://datasets/kirillgoltsman/titled-tuesday-chess-games/titled-tuesday.csv",
            dtype={"tournament": "string"}
        ),
        #"2-million-user-games": dd.read_csv(
        #    "data\\user-games.csv",
        #    sep=';',
        #    dtype={'time_control': 'string'}
        #),
    }
    end = time.time()
    length = end - start
    print(f"Time to load dataframes: {length}")
    #dfs[USRGAMES] = dfs[USRGAMES].loc[(dfs[USRGAMES]['rating_white'] < 3999) & (dfs[USRGAMES]['rating_black'] < 4000)]

    dfs = pre_processing(dfs)

    return dfs

def pre_processing(dfs):
    # TODO: Fix dropna to only drop certain features
    dfs[constants.TT].dropna(subset=['username', 'accuracy', 'rating', 'rank', 'tournament'])
    dfs[constants.TT].loc[(dfs[constants.TT]!=0).any(axis=1)]

    #dfs[constants.USRGAMES].dropna(subset=['white', 'end_date', 'white_elo'])
    #dfs[constants.USRGAMES].loc[(dfs[constants.USRGAMES]!=0).any(axis=1)]

    return dfs