import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/src/utils')

from datetime import datetime
from common import getCsvFiles, readFile
import pandas as pd

def detect(location, date):
    csvFiles = getCsvFiles(location)
    # csvFiles = ['VCB.csv']
    candidates = []
    minPrices = []
    maxPrices = []
    for file in csvFiles:
        df = readFile((location + file))
        positions = df.index.get_loc(str(date))
        if len(positions) == 0:
            continue
        
        position = positions[0]
        if position >= len(df) - 12:
            continue
        flowDf = df.iloc[position:position + 2]
        subDf = df.iloc[position + 2:position + 10]
        meanVol = subDf.Volume.mean()
        if meanVol > 25000 and flowDf.iloc[0].Change > 0 and flowDf.iloc[0].Volume > meanVol * 2 \
            and flowDf.iloc[1].Change > 0 and flowDf.iloc[1].Volume > meanVol * 2:
            candidates.append(file[0:3])
    if len(candidates) > 0:
        return (str(date), ','.join(candidates))
if __name__ == '__main__':
    # print(detect('./data/all/', '2020-05-26'))
    start = '2019-01-01'
    end = '2019-12-31'
    dates = pd.date_range(start, end).tolist()
    for date in dates:
        print(str(date)[0:10], detect('./data/all/', str(date)[0:10]))
