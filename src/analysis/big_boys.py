import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/src/utils')

from datetime import datetime
from common import getCsvFiles, readFile
import pandas as pd

def detect(location, start, end):
    csvFiles = getCsvFiles(location)
    # csvFiles = ['VCB.csv']
    stocks = []
    startPrices = []
    endPrices = []
    changes = []
    volumes = []
    vcb = readFile((location + 'VCB.csv')).loc[end:start]
    for file in csvFiles:
        df = readFile((location + file))
        subDf = df.loc[end:start]
        if len(vcb) > len(subDf):
            continue
        subDf = subDf[['Close', 'Volume']]
        stocks.append(file[0:3])
        endPrices.append(subDf.iloc[0].Close)
        startPrices.append(subDf.iloc[-1].Close)
        volumes.append(subDf.iloc[0:5].Volume.mean())
        changes.append(round((subDf.iloc[0].Close - subDf.iloc[-1].Close) / subDf.iloc[-1].Close * 100, 2))
    df = pd.DataFrame.from_dict({
        'Stock': stocks,
        'Start': startPrices, 
        'End': endPrices, 
        'Change': changes,
        'Volume': volumes
    })
    df.set_index('Stock', inplace=True)
    df.sort_values(by='Change', ascending=False, inplace=True)
    df.to_csv('./reports/big_boys.csv')

def findDriver(location, start, end):
    csvFiles = getCsvFiles(location)
    # csvFiles = ['VCB.csv']
    stocks = []
    startPrices = []
    endPrices = []
    changes = []
    volumes = []
    vcb = readFile((location + 'VCB.csv')).loc[end:start]
    dates = pd.date_range(start, end).tolist()
    
    for file in csvFiles:
        df = readFile((location + file))
        appearances = []
        for date in dates:
            date = str(date)[0:10]
            positions = df.index.get_loc(date)
            if len(positions) == 0:
                continue
            position = positions[0]
            if position >= len(df) - 14:
                continue
            threeDayDf = df.iloc[position:position+3]
            tenDayDf = df.iloc[position+3:position+13]
            if threeDayDf.Volume.mean() > tenDayDf.Volume.mean() and threeDayDf.Volume.min() > tenDayDf.Volume.max()\
                and tenDayDf.Volume.min() > 100000 and threeDayDf.Change.max() > 4:
                appearances.append(date)
        if len(appearances) > 0:
            print(file[0:3], '|'.join(appearances))

def findDailyWaves(location, date):
    csvFiles = getCsvFiles(location)
    # csvFiles = ['TTB.csv']
    stocks = []
    startPrices = []
    endPrices = []
    changes = []
    volumes = []
    appearances = []
    for file in csvFiles:
        df = readFile((location + file))
        df['CE'] = df.Change.apply(lambda x: x > 6)
        date = str(date)[0:10]
        positions = df.index.get_loc(date)
        if len(positions) == 0:
            continue
        position = positions[0]
        if position >= len(df) - 3:
            continue
        subDf = df.iloc[position:position+2]
        # print(subDf['Change'])
        
        if subDf.CE.sum() > 0 and subDf.Change.min() > 0 and subDf.Volume.min() > 100000 and subDf.Close.min() > 2:
            appearances.append(file[0:3])
        
    if len(appearances) > 0:
        print(date, '|'.join(appearances))

def researchPenny(location, start, end):
    csvFiles = getCsvFiles(location)
    # csvFiles = ['VCB.csv']
    stocks = []
    startPrices = []
    endPrices = []
    changes = []
    volumes = []
    vcb = readFile((location + 'VCB.csv')).loc[end:start]
    for file in csvFiles:
        df = readFile((location + file))
        subDf = df.loc[end:start]
        if (len(vcb) > len(subDf)):
            continue
        if  (subDf.iloc[-1].Close > 5) or (subDf.iloc[0].Volume < 500000):
            continue
        subDf = subDf[['Close', 'Volume']]
        stocks.append(file[0:3])
        endPrices.append(subDf.iloc[0].Close)
        startPrices.append(subDf.iloc[-1].Close)
        volumes.append(subDf.iloc[0:5].Volume.mean())
        changes.append(round((subDf.iloc[0].Close - subDf.iloc[-1].Close) / subDf.iloc[-1].Close * 100, 2))
    df = pd.DataFrame.from_dict({
        'Stock': stocks,
        'Start': startPrices, 
        'End': endPrices, 
        'Change': changes,
        'Volume': volumes
    })
    df.set_index('Stock', inplace=True)
    df.sort_values(by='Change', ascending=True, inplace=True)
    df.to_csv('./reports/valuable/penny_report.csv')

def researchBlue(location, start, end):
    csvFiles = getCsvFiles(location)
    # csvFiles = ['VCB.csv']
    stocks = []
    startPrices = []
    endPrices = []
    changes = []
    volumes = []
    vcb = readFile((location + 'VCB.csv')).loc[end:start]
    for file in csvFiles:
        df = readFile((location + file))
        subDf = df.loc[end:start]
        if (len(vcb) > len(subDf)):
            continue
        if  (subDf.iloc[-1].Close < 10) or (subDf.iloc[0].Volume < 500000):
            continue
        subDf = subDf[['Close', 'Volume']]
        stocks.append(file[0:3])
        endPrices.append(subDf.iloc[0].Close)
        startPrices.append(subDf.iloc[-1].Close)
        volumes.append(subDf.iloc[0:5].Volume.mean())
        changes.append(round((subDf.iloc[0].Close - subDf.iloc[-1].Close) / subDf.iloc[-1].Close * 100, 2))
    df = pd.DataFrame.from_dict({
        'Stock': stocks,
        'Start': startPrices, 
        'End': endPrices, 
        'Change': changes,
        'Volume': volumes
    })
    df.set_index('Stock', inplace=True)
    df.sort_values(by='Change', ascending=True, inplace=True)
    df.to_csv('./reports/valuable/blue_report.csv')

def cashFlow(location, date):
    csvFiles = getCsvFiles(location)
    # csvFiles = ['HVN.csv']
    stocks = []
    for file in csvFiles:
        df = readFile((location + file))
        positions = df.index.get_loc(date)
        if len(positions) == 0:
            continue
        position = positions[0]
        if position >= len(df) - 20:
            continue
        df.sort_index(ascending=True, inplace=True)
        df['MaVol'] = df.Volume.rolling(20).mean()
        df.sort_index(ascending=False, inplace=True)
        subDf = df.iloc[position:position+20]
        count = 0
        for i in range(10):
            
            if subDf.iloc[i].Volume < subDf.iloc[i].MaVol\
                and (subDf.iloc[position:position+10].Close.mean() < subDf.iloc[position+10:position+20].Close.mean() * 1.1)\
                and subDf.iloc[position].Close < 10 and subDf.iloc[position].MaVol > 100000:
                count = count + 1
        if count > 7:
            stocks.append(file[0:3])
    if len(stocks) > 0:
        stocks.sort()
        print(date, ','.join(stocks))
    return stocks

    # csvFiles = ['VCB.csv']
    



if __name__ == '__main__':
    # df = detect('./data/all/', '2020-04-20', '2020-04-27')
    # df = findDriver('./data/historical/', '2020-05-01', '2020-05-27')

    # findDailyWaves('./data/all/','2020-05-28')
    # researchPenny('./data/all/', '2020-03-31', '2020-05-28')
    # researchBlue('./data/all/', '2020-03-31', '2020-05-28')
    cashFlow('./data/all/','2020-05-28')