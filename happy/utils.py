from icecream import ic
import logging
import sh
import glob
from common import getCsvFiles, readRawFile, readFile, getConfigParser

def getInvestingVolume(price, investingMoney, investingAmount, maxStock):
    if(investingAmount - investingMoney) < 10000000:
        return 0;
    stockVolume = round((investingAmount - investingMoney)/price);
    if stockVolume > maxStock:
        stockVolume = maxStock
    stockVolume -= stockVolume % -50
    return stockVolume;

def getTradeFee(value, tradeRate):
    return round(value * tradeRate, 0)

def selectStocks(year):
    parser = getConfigParser()
    BASED_DIR = parser.get('happy', 'based_dir')
    SOURCE_LOCATION = BASED_DIR + parser.get('happy', 'source_location')
    SELECTED_STOCK_LOCATION = BASED_DIR + parser.get('happy', 'selected_stock_location')
    NUMBER_OF_DAYS = int(parser.get('happy', 'active_days'))
    MIN_VOLUME = int(parser.get('happy', 'min_volume'))
    MIN_OPEN_PRICE = int(parser.get('happy', 'min_open_price'))
    MAX_OPEN_PRICE = int(parser.get('happy', 'max_open_price'))

    if len(getCsvFiles(SELECTED_STOCK_LOCATION)) > 0:
        sh.rm(glob.glob(SELECTED_STOCK_LOCATION + "*"))
    ic("Started selecting stocks...")
    csvFiles = getCsvFiles(SOURCE_LOCATION);
    # csvFiles = ["AAA.csv","APG.csv"]
    selected = []
    for file in csvFiles:
        df = readFile((SOURCE_LOCATION + "{}").format(file));
        df = df.loc[year]
        if(len(df) > NUMBER_OF_DAYS) and df.Volume.mean() > MIN_VOLUME and (df.Open.mean() > MIN_OPEN_PRICE and df.Open.mean() < MAX_OPEN_PRICE):
            df["Short"] = False
            df["Long"] = False
            df["Categories"] = ""
            df["Recommendation"] = ""
            df["Action"] = ""
            df.to_csv((SELECTED_STOCK_LOCATION + "{}").format(file))
    ic("Completed selecting stocks!")

def getPrice(record, strategy):
    if strategy == "OPEN":
        return record.Open
    elif strategy == "MEAN":
        return round((record.Open + record.Close)/2)
    else:
        return record.Close
