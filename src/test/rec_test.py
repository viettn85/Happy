import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/src/happy')

from recommender import recommendMA
from datetime import datetime
import pandas as pd
start = '2020-01-01'
today = datetime.today().strftime("%Y-%m-%d")
dates = pd.date_range(start, today).tolist()

for date in dates:
    recommendMA(str(date)[0:10])
