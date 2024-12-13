'''
Common constants that are used between files
'''

# Paths
PROCESSED_DATA_PATH = "data"

# Dataframe simplification
TT = "titled-tuesday"
TT_W = "titled-tuesday-winners"
USRGAMES = "2-million-user-games"
GMLATEST = "gm-latest"
GMACCU = "gm-accuracy"

# Time control lookup
TIME_CONTROLS = ["1 min", "1|1", "2|1", "3 min", "3|2", "5 min", "10 min", "15|10", "30 min"] # There are a lot more.. these are the top ones
TIME_CONTROLS_MAP = {
    "1 min": "60",
    "1|1": "60+1",
    "2|1": "120+1",
    "3 min": "180",
    "3|2": "180+2",
    "5 min": "300",
    "10 min": "600",
    "15|10": "900+10",
    "30 min": "1800"
}
