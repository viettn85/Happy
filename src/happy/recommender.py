import sys
sys.path.insert(1, '/Users/viet_tran/Workplace/Practice/Happy/src/utils')

import pandas as pd
from common import getCsvFiles, readFile
import logging
import logging.config
from datetime import datetime

pd.options.mode.chained_assignment = None 
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()


def recommendPatterns(date):
    pass

def recommendMA(date):
    logger.info("Started recommendation process on {}".format(date))
    csvFiles = getCsvFiles("./data/historical/")
    csvFiles = ['BID.csv']
    sell = []
    buy = []
    buyMore = []
    for f in csvFiles:
        df = readFile(("./data/historical/" + f))
        positions = df.index.get_loc(str(date))
        if len(positions) == 0:
            continue
        position = positions[0]
        row = df.iloc[position]
        recommendation = ""
        stock = f[0:3]
        print(df.iloc[position + 1].MA3, df.iloc[position].MA3)
        print(df.iloc[position + 1].MA3_8, df.iloc[position].MA3_8)
        # if (stock == 'BID'):
        #     print(df.iloc[position + 1].MA3, df.iloc[position].MA3)
        if df.iloc[position].MA3_8 < 0:
            if df.iloc[position + 1].MA3_8 >= 0:
                recommendation = "Start Buying"
                buy.append(stock)
            elif df.iloc[position + 1].MA3 + 0.1 > df.iloc[position].MA3:
                print("Selling date {} for {}".format(date, stock))
                recommendation = "Start Selling"
                sell.append(stock)
            else:
                recommendation = "Continue Buying"
                buyMore.append(stock)
        else:
            if df.iloc[position + 1].MA3_8 < 0:
                recommendation = "Start Selling"
                sell.append(stock)
            else:
                recommendation = "Continue Watching"
        # Update recommendation
        # logger.info((recommendation, df.iloc[position + 1].MA3_8, df.iloc[position].MA3_8))
        df.Recommendation.iloc[position] = recommendation
        df.to_csv("./data/historical/" + f)
    # Update REC reports
    rec = readFile("./reports/rec.csv")
    rec.loc[datetime.strptime(date, "%Y-%m-%d")] = ['|'.join(sell), '|'.join(buy), '|'.join(buyMore)]
    rec.sort_index(ascending=False, inplace=True)
    rec.to_csv('./reports/rec.csv')
    logger.info("Ended recommendation process on {}".format(date))


if __name__ == '__main__':
    date = "2020-05-20"
    recommendMA(date)
