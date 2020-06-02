import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/src/utils')

from datetime import datetime
from common import getCsvFiles, readFile
import pandas as pd

def fastRecover(location, times):
    csvFiles = getCsvFiles(location)
    # csvFiles = ['VCB.csv']
    candidates = []
    minPrices = []
    maxPrices = []
    for file in csvFiles:
        df = readFile((location + file))
        lowestWeeks = df.loc['2020-04-03':'2020-03-24']
        minPrice = lowestWeeks.Close.min()
        april = df.loc['2020-04']
        maxPrice = april.Close.max()
        if maxPrice > times * minPrice:
            candidates.append(file[0:3])
            minPrices.append(str(minPrice))
            maxPrices.append(str(maxPrice))
    df = pd.DataFrame.from_dict({"Stock": candidates, "MinPrice": minPrices, "MaxPrice": maxPrices})
    print("Increase more than {} times in one month:".format(times))
    print(','.join(candidates))
    df.to_csv('./reports/analysis/fast_recover_{}_times.csv'.format(times))

def slowRecover(location, times):
    csvFiles = getCsvFiles(location)
    # csvFiles = ['VCB.csv']
    candidates = []
    minPrices = []
    maxPrices = []
    for file in csvFiles:
        df = readFile((location + file))
        lowestWeeks = df.loc['2020-04-03':'2020-03-24']
        minPrice = lowestWeeks.Close.min()
        april = df.loc[:'2020-04']
        maxPrice = april.Close.max()
        if maxPrice < times * minPrice:
            candidates.append(file[0:3])
            minPrices.append(str(minPrice))
            maxPrices.append(str(maxPrice))
    df = pd.DataFrame.from_dict({"Stock": candidates, "MinPrice": minPrices, "MaxPrice": maxPrices})
    print("Increase less than {} times in one month:".format(times))
    print(','.join(candidates))
    df.to_csv('./reports/analysis/slow_recover_{}_times.csv'.format(times))

def lost2020(location, times):
    csvFiles = getCsvFiles(location)
    # csvFiles = ['VCB.csv']
    candidates = []
    minPrices = []
    maxPrices = []
    for file in csvFiles:
        df = readFile((location + file))
        df2020 = df.loc['2020']
        df2019 = df.loc['2019']
        if df2020.Close.max() * times < df2019.Close.max():
            candidates.append(file[0:3])
            minPrices.append(str(df2020.Close.max()))
            maxPrices.append(str(df2019.Close.max()))
    df = pd.DataFrame.from_dict({"Stock": candidates, "2020": minPrices, "2019": maxPrices})
    print("2019 more than {} times 2020:".format(times))
    print(','.join(candidates))
    df.to_csv('./reports/analysis/2019_{}_times_2020.csv'.format(times))

def lost2020(location):
    csvFiles = getCsvFiles(location)
    stocks = []
    for file in csvFiles:
        df = readFile((location + file))
        df2020 = df.loc['2020']
        if df2020.Close.iloc[0] > 3 and df2020.Close.iloc[0] <= 5:
            stocks.append(file[0:3])
    return ','.join(stocks)
    # FTS
if __name__ == '__main__':
    # fastRecover('./data/all/', 2)
    # fastRecover('./data/all/', 1.5)
    # slowRecover('./data/all/', 1.2)
    # lost2020('./data/all/', 2)
    # lost2020('./data/all/', 4)
    print(lost2020('./data/all/'))