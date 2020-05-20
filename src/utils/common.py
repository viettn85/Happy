import os
import pandas as pd
from configparser import ConfigParser
from icecream import ic
import logging
import sh
import glob

def getConfigParser():
    parser = ConfigParser()
    parser.read('happy.ini')
    return parser

def getRate():
    parser = getConfigParser()
    return int(parser.get('happy', 'candle_rates'))

def getCsvFiles(location):
        try:
            entries = os.listdir(location)
            return list(filter(lambda x: os.path.splitext(x)[1], entries))
        except:
            print("Something wrong with file location: {}".format(location))

def readFile(f):
    dateParser = lambda x: pd.datetime.strptime(x, "%Y-%m-%d")
    df = pd.read_csv(f, parse_dates=True, index_col="Date", date_parser=dateParser)
    # df = pd.read_csv(f, parse_dates=True, index_col="Date")
    return df

def readReport(f):
    df = pd.read_csv(f, index_col="ID")
    return df

def readRawFile(f):
    df = pd.read_csv(f)
    return df

def writeShortFile(df, f):
    df.to_csv(f)


# START: Only for testing
def clearFileContent(file):
    df = readRawFile(file)
    df.iloc[0:0].to_csv(file,index=None)

def clearReports():
    parser = getConfigParser()
    BASED_DIR = parser.get('happy', 'based_dir')
    REPORT_LOCATION = BASED_DIR + parser.get('happy', 'report_location')
    clearFileContent(REPORT_LOCATION + "trade_report.csv")
    clearFileContent(REPORT_LOCATION + "stock_rec_report.csv")
    clearFileContent(REPORT_LOCATION + "portfolio.csv")

def clearRecFolders():
    parser = getConfigParser()
    BASED_DIR = parser.get('happy', 'based_dir')
    REC_FULL_LOCATION = BASED_DIR + parser.get('happy', 'rec_full_location')
    REC_ACTIONS_LOCATION = BASED_DIR + parser.get('happy', 'rec_actions_location')
    if len(getCsvFiles(REC_FULL_LOCATION)) > 0:
        ic("Clean rec folder")
        sh.rm(glob.glob(REC_FULL_LOCATION + "*"))
    if len(getCsvFiles(REC_ACTIONS_LOCATION)) > 0:
        ic("Clean rec_actions folder")
        sh.rm(glob.glob(REC_ACTIONS_LOCATION + "*"))

# END: Only for testing