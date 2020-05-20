from identify_candlestick import recognize_candlestick
from candle_rankings import *
import pandas as pd
import os
from icecream import ic


def countSignals(file):
    df = pd.read_csv(file, parse_dates=True, index_col="Date")
    try:
        df = df.loc["2020"]
        if len(df) == 0:
            return 0
        df = recognize_candlestick(df)
        # df['Bull_Signals'] = df.candlestick_pattern.apply(lambda x: getRank(x) < 30 and '_Bull' in x)
        # df['Bear_Signals'] = df.candlestick_pattern.apply(lambda x: getRank(x) < 50 and '_Bear' in x)
        df['Bad_Signals'] = df.candlestick_pattern.apply(lambda x: getDuckyRanks(x) < 50)
        # bullDf = df[df.Bull_Signals]
        # bearDf = df[df.Bear_Signals]
        # return (file, len(bullDf), len(bearDf), len(df[df.Bad_Signals]))
        print(df[df.Bad_Signals])
        return len(df[df.Bad_Signals])
    except:
        return 0


def countAll():
    entries = os.listdir("/Users/viet_tran/Workplace/Practice/VNStock/d3_data/")
    files = list(filter(lambda x: os.path.splitext(x)[1], entries))
    files = ['PVD.csv']
    stocks = []
    counts = []
    for file in files:
        ic(file)
        stocks.append(file[-7:-4])
        counts.append(countSignals("/Users/viet_tran/Workplace/Practice/VNStock/d3_data/{}".format(file)))
    df = pd.DataFrame.from_dict({
        "Stock": stocks,
        "Count": counts
    })
    df.sort_values(by=['Count'], inplace=True)
    df.to_csv('counts.csv')
    

countAll()