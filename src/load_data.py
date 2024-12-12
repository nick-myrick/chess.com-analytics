import time
import dask.dataframe as dd
import constants

def load(dfs):
    print("Loading dataframes")
    start = time.time()
    dfs = {
        "titled-tuesday": dd.read_csv(
            "hf://datasets/kirillgoltsman/titled-tuesday-chess-games/titled-tuesday.csv",
            dtype={"tournament": "string"}
        ),
        #"2-million-user-games": dd.read_parquet(
        #    "data\\2-million-games.parquet"
        #),
        "2-million-user-games": dd.read_csv(
            "data\\user-games.csv",
            sep=';',
            dtype={'time_control': 'string'}
        ),
        "gm-latest": dd.read_csv(
            "data\\gm-games-latest.csv",
            usecols=[
                'Date','White','Black','BlackElo','WhiteElo'
            ]
        ), # Up to 2023
        "gm-accuracy": dd.read_csv(
            "data\\gm-games-accuracy.csv",
            usecols=[
                'player','player_name','white_Accuracy','black_Accuracy','Date','WhiteElo','BlackElo'
            ]
        ) # Only up to 2021, note: most games don't have accuracy?
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
    #dfs[USRGAMES].dropna(subset=['rating_white', 'rating_black', 'date'])
    dfs[constants.USRGAMES].dropna(subset=['white', 'end_date', 'white_elo'])
    dfs[constants.GMLATEST].dropna(subset=['WhiteElo', 'BlackElo', 'White', 'Black'])
    dfs[constants.GMACCU].dropna(subset=['WhiteElo', 'BlackElo', 'player_name'])
    return dfs