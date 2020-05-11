import os
import pandas as pd
from configparser import ConfigParser
from icecream import ic
import logging
import sh
import glob

def getCsvFiles(location):
        try:
            entries = os.listdir(location)
            return list(filter(lambda x: os.path.splitext(x)[1], entries))
        except:
            print("Something wrong with file location: {}".format(location))

def readFile(f):
    # dateParser = lambda x: pd.datetime.strptime(x, "%d/%m/%Y")
    # df = pd.read_csv(f, parse_dates=True, index_col="Date", date_parser=dateParser);
    df = pd.read_csv(f, parse_dates=True, index_col="Date");
    return df;

def readRawFile(f):
    df = pd.read_csv(f);
    return df;

def writeShortFile(df, f):
    df.to_csv(f)

def getConfigParser():
    parser = ConfigParser()
    parser.read('happy.ini')
    return parser

def preproceed(location, d3Data):
    logging.info("Started preproceeding process...")
    ic("Started preproceeding process...")
    csvFiles = getCsvFiles(location);
    for f in csvFiles:
        df = readRawFile((location + f));
        if not {'Date', 'Close', "High", "Low", "Open", "Volume"}.issubset(df.columns):
            os.remove(location + f)
            ic("Removed", f)
            logging.info("Removed raw stock {}".format(f))
            continue
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index("Date", inplace=True)
        df.sort_index(ascending=False, inplace=True)
        df["Change"] = round(abs(df.Close - df.Open)/df.Open * 100, 2);
        df = df[["Close", "Open", "High", "Low", "Change", "Volume"]]
        df.to_csv(location + f)
        df.sort_index(ascending=True, inplace=True)
        df.to_csv(d3Data + f)
    logging.info("Completed preproceeding process...")
    ic("Completed preproceeding process...")

# START: Only for testing
def clearFileContent(file):
    df = readRawFile(file);
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