from common import getConfigParser
from icecream import ic

def isRed(df, index):
    if index >= len(df):
        return False
    c = df.iloc[index]
    return c.Open > c.Close

def isGreen(df, index):
    if index >= len(df):
        return False
    c = df.iloc[index]
    return c.Close > c.Open

def isFull(high, top, bottom, low, RATE): # Use to check if the canlde stills if full both sides
    return (top - bottom) > RATE * (high - top) and (top - bottom) > RATE * (bottom - low)

def isTopFull(high, top, bottom, low, RATE):
    return (top - bottom) > RATE * (high - top) and (top - bottom) <= RATE * (bottom - low)

def isBottomFull(high, top, bottom, low, RATE):
    return (top - bottom) <= RATE * (high - top) and (top - bottom) > RATE * (bottom - low)

def isLongGreen(df, index):
    if index >= len(df):
        return False
    c = df.iloc[index]
    return c.Close > c.Open and c.Change >= 6.5

def isFullRed(df, index, RATE):
    if index >= len(df):
        return False
    c = df.iloc[index]
    return isFull(c.High, c.Open, c.Close, c.Low, RATE)

def isFullGreen(df, index, RATE):
    if index >= len(df):
        return False
    c = df.iloc[index]
    return isFull(c.High, c.Close, c.Open, c.Low, RATE) and c.Change > 3

def isUpRed(df, index, RATE):
    if index >= len(df):
        return False
    c = df.iloc[index]
    return isTopFull(c.High, c.Open, c.Close, c.Low, RATE)

def isUpGreen(df, index, RATE):
    if index >= len(df):
        return False
    c = df.iloc[index]
    return isTopFull(c.High, c.Close, c.Open, c.Low, RATE) and c.Change > 3

def isDownRed(df, index, RATE):
    if index >= len(df):
        return False
    c = df.iloc[index]
    return isBottomFull(c.High, c.Open, c.Close, c.Low, RATE)

def isDownGreen(df, index, RATE):
    if index >= len(df):
        return False
    c = df.iloc[index]
    return isBottomFull(c.High, c.Close, c.Open, c.Low, RATE)

def isDoji(df, index):
    if index >= len(df):
        return False
    c = df.iloc[index]
    return c.Open == c.Close

def isBalancedDoji(df, index):
    if index >= len(df):
        return False
    c = df.iloc[index]
    return (c.Open == c.Close) and abs(c.High - c.Open) == abs(c.Low - c.Open)

def isUpDoji(df, index):
    if index >= len(df):
        return False
    c = df.iloc[index]
    return (c.Open == c.Close) and (c.High == c.Open)

def isDownDoji(df, index):
    if index >= len(df):
        return False
    c = df.iloc[index]
    return (c.Open == c.Close) and (c.Low == c.Open)

def isInscreasingTrend(df, index): # If the current day's high and mean are higher that previous day's
    if index >= len(df) - 1:
        return False
    c = df.iloc[index]
    p = df.iloc[index + 1]
    return c.MA3_20 < 0 and (c.Close > p.Close) and ((c.Close + c.Open) > (p.Close + p.Open))

def isOverProfit(df, position, stock, portfolio):
    c = df.iloc[position]
    if stock in portfolio.index:
        
        parser = getConfigParser()
        overcomeProfitRate = float(parser.get('happy', 'over_profit_rate'))
        boughtPrice = portfolio.loc[stock].Price
        profitThreshold = boughtPrice * (1 + overcomeProfitRate)
        # ic("---isOverProfit {} {} {} {}".format(boughtPrice, profitThreshold, c.Open, c.Close))
        if  min(c.Open, c.Close) < profitThreshold and profitThreshold < max(c.Open, c.Close):
            return True
        if isDoji(df, position) and min(c.Open, c.Close) > profitThreshold:
            return True
    return False

def isCutLoss(df, position, stock, portfolio):
    c = df.iloc[position]
    if stock in portfolio.index:
        parser = getConfigParser()
        cutLossRate = float(parser.get('happy', 'cut_loss_rate'))
        boughtPrice = portfolio.loc[stock].Price
        cutLossThreshold = boughtPrice * (1 - cutLossRate)
        # ic("---isCutLoss {} {} {} {}".format(boughtPrice, cutLossThreshold, c.Open, c.Close))
        if min(c.Open, c.Close) < cutLossThreshold and cutLossThreshold < max(c.Open, c.Close):
            return True
        if isDoji(df, position) and max(c.Open, c.Close) < cutLossThreshold:
            return True

    return False

def isSpecialReversalToUpTrend(df, index):
    if index >= len(df) - 2:
        return False;
    c = df.iloc[index]
    p1 = df.iloc[index + 1]
    p2 = df.iloc[index + 2]
    if (p1.Category == "Down Doji" or (p1.Category == "Down Red" and p1.Short)) \
        and (p2.Category == "Down Red" or p2.Category == "Down Doji") \
        and ((p2.MA3 - p1.MA3) > (p1.MA3 - c.MA3)):
        return True
    return False
