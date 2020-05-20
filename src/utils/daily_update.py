import pandas as pd
import logging
import logging.config
from datetime import datetime
from categorization import categorizeCandle
from utils import calculateMAs
from common import readFile
from configparser import ConfigParser

pd.options.mode.chained_assignment = None 
logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger()

LINK = 'https://s.cafef.vn/Lich-su-giao-dich-{}-1.chn'
RAW_NAME = ['Ngày', 'Giá đóng cửa', 'GD khớp lệnh', 'Giá mở cửa', 'Giá cao nhất', 'Giá thấp nhất']
NEW_NAME = ["Date", "Close", 'Volume', 'Value', "Open", "High", "Low"]
ORDERED = ['Close', 'Open', 'High', 'Low', 'Volume']
FULL = ['Close', 'Open', 'High', 'Low', 'Change', 'Volume', 'MA3', 'MA8', 'MA20',\
            'MA3_8', 'MA3_20', 'MA8_20', 'Short', 'Long', 'Category', 'Recommendation', 'Action']
class Crawl:
    def __init__(self, mck):
        self.mck = mck
        self.link = LINK.format(self.mck)
        self.df_old, self.df_new = None, None

    @staticmethod
    def clean(df):
        df.columns = df.iloc[0, :].values
        df = df.loc[2:, :][RAW_NAME]
        df.columns = NEW_NAME
        
        df["Date"] = pd.to_datetime(df["Date"], format='%d/%m/%Y')
        df.set_index("Date", inplace=True)
        for col in df.columns:
            df[col] = pd.to_numeric(df[col])
        df = df[ORDERED]
        return df

    def get_response(self):
        logger.info("Getting new data of {}".format(self.mck))
        df_new = pd.read_html(self.link, encoding='utf-8')[1]
        df_new = self.clean(df_new)
        df_new.sort_index(ascending=True, inplace=True)
        calculateMAs(df_new)
        df_new.sort_index(ascending=False, inplace=True)
        df_new['Change'] = 0
        df_new['Short'] = 'False'
        df_new['Long'] = 'False'
        df_new['Category'] = ''
        df_new['Recommendation'] = ''
        df_new['Action'] = ''
        # Categorize
        for i in range(len(df_new)):
            categorizeCandle(df_new, i)
        logger.info("Completed getting new data of {}".format(self.mck))
        return df_new

    def merger_to_old_data(self):
        self.df_new = self.get_response()
        self.df_old = readFile("./data/historical/{}.csv".format(self.mck))
        df_gap = self.df_new.loc[:self.df_old.index.values[0],:][0:-1]
        df_gap = df_gap[FULL]
        df = df_gap.append(self.df_old)
        return df

    def run(self):
        logger.info("Started updating {}".format(self.mck))
        df = self.merger_to_old_data()
        # Update D3 Data
        df.sort_index(ascending=True, inplace=True)
        calculateMAs(df)
        df.to_csv('./data/d3/{}.csv'.format(self.mck))
        # Update Historical Data
        df.sort_index(ascending=False, inplace=True)
        df.to_csv('./data/historical/{}.csv'.format(self.mck))
        logger.info("Ended updating {}".format(self.mck))

if __name__ == '__main__':
    stocks = pd.read_csv('../stock.csv')
    stocks = stocks.values
    for index, stock in stocks:
        try:
            logger.info((index, stock))
            Crawl(stock).run()
        except Exception as e:
            logger.error(e)

