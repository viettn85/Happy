from common import *
from rules import *
from icecream import ic

pd.options.mode.chained_assignment = None 

def extract4Days(df, position):
    c = df.iloc[position]
    t1 = df.iloc[position - 1]
    t2 = df.iloc[position - 2]
    t3 = df.iloc[position - 3]
    return (c, t1, t2. t3)

def getTradePrice(df, position):
    if isGreen(df, position):
        return df.iloc[position].High
    elif isRed(df, position):
        return df.iloc[position].Low
    else:
        return df.iloc[position].High
    

def isContinuousIncrease(df, position):
    pc = getTradePrice(df, position)
    pt1 = getTradePrice(df, position - 1)
    pt2 = getTradePrice(df, position - 2)
    pt3 = getTradePrice(df, position - 3)
    # if (pc <= pt1) and (pt1 <= pt2) and (pt2 <= pt3):
    #     ic("Continuous Increase")
    # return ((pc <= pt1) and (pt1 <= pt2) and (pt2 <= pt3)) ? 1 : 0
    return (pc <= pt1) and (pt1 <= pt2) and (pt2 <= pt3)


def isTradable(df, position):
    pc = getTradePrice(df, position)
    pt3 = getTradePrice(df, position - 3)
    # if (pc <= pt3):
    #     ic("Tradable")
    # return (pc <= pt3) ? 1 : 0
    return pc <= pt3

def getTrend(row):
    trend = row.Close - row.Open
    return  "Increasing" if trend > 0 else "Decreasing"

def getShape(df, position):
    parser = getConfigParser()
    RATE = int(parser.get('happy', 'candle_rates'))
    if isGreen(df, position):
        if isFullGreen(df, position, RATE):
            return "Full Green"
        elif isUpGreen(df, position, RATE):
            return "Up Green"
        elif isDownGreen(df, position, RATE):
            return "Down Green"
        else:
            return "Green"
    elif isRed(df, position):
        if isFullRed(df, position, RATE):
            return "Full Red"
        elif isUpRed(df, position, RATE):
            return "Up Red"
        elif isDownRed(df, position, RATE):
            return "Down Red"
        else:
            return "Red"
    else:
        if isBalancedDoji(df, position):
            return "Balanced Doji"
        elif isUpDoji(df, position):
            return "Up Doji"
        elif isDownDoji(df, position):
            return "Down Doji"
        else:
            return "Doji"

def generateTradableValue():
    parser = getConfigParser()
    BASED_DIR = parser.get('happy', 'based_dir')
    SELECTED_STOCK_LOCATION = BASED_DIR + parser.get('happy', 'selected_stock_location')
    TRADABLE_LOCATION = BASED_DIR + parser.get('happy', 'tradable_location')
    TRADABLE_LOCATION = BASED_DIR + parser.get('happy', 'tradable_location')
    REPORT_LOCATION = BASED_DIR + parser.get('happy', 'report_location')
    NEW_SHAPES_LOCATION = BASED_DIR + parser.get('happy', 'new_shapes_location')
    files = getCsvFiles(SELECTED_STOCK_LOCATION)
    # files = ['TCH.csv']
    stocks = []
    tradable = []
    continuousIncrease = []
    for file in files:
        ic(file)
        df = readFile(SELECTED_STOCK_LOCATION + file)
        df['Tradable'] = False
        df['ContinuousIncrease'] = False
        df['Trend'] = df.apply (lambda row: getTrend(row), axis=1)
        df['Shape'] = ''
        for i in reversed(range(len(df) - 4)):
            position = i + 3
            # if isContinuousIncrease(df, position):
            #     ic("Before")
            #     ic(df.iloc[position])
            df.Tradable.iloc[position] = isTradable(df, position)
            df.ContinuousIncrease.iloc[position] = isContinuousIncrease(df, position)
            df.Shape.iloc[position] = getShape(df, position)
            # if isContinuousIncrease(df, position):
            #     ic("After")
            #     ic(df.iloc[position])
        df = df[['Close','High','Low', 'Trend', 'Shape', 'Recommendation', 'Tradable', 'ContinuousIncrease']]
        df.to_csv(TRADABLE_LOCATION + file)
        tradable.append(df.Tradable.sum())
        continuousIncrease.append(df.ContinuousIncrease.sum())
        # Create previous shape columns
        df['Shape1'] = df.Shape.shift(-1)
        df['Shape2'] = df.Shape.shift(-2)
        df['Shape3'] = df.Shape.shift(-3)
        df['Shape4'] = df.Shape.shift(-4)
        df['Shape5'] = df.Shape.shift(-5)
        df['Shape6'] = df.Shape.shift(-6)
        df['Shape7'] = df.Shape.shift(-7)
        df = df[['Shape1', 'Shape2', 'Shape3', 'Shape4', 'Shape5', 'Shape6', 'Shape7', 'Tradable']]
        df.dropna(inplace=True, how='any')
        df.to_csv(NEW_SHAPES_LOCATION + file)
    trandableReport = pd.DataFrame.from_dict({
        "Stock": files,
        "Tradable": tradable,
        "ContinuousIncrease": continuousIncrease
    })
    trandableReport.to_csv(REPORT_LOCATION + "tradable.csv")

generateTradableValue()
