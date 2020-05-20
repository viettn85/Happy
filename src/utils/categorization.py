from rules import *
from common import getRate

def categorizeCandle(df, position):
    RATE = getRate()
    category = ""
    if isGreen(df, position):
        if isFullGreen(df, position, RATE):
            category = "Full Green"
        elif isUpGreen(df, position, RATE):
            category = "Up Green"
        elif isDownGreen(df, position, RATE):
            category = "Down Green"
        elif df.iloc[position].Short:
            category = "Short Green"
        else:
            category = "Green"
    elif isRed(df, position):
        if isFullRed(df, position, RATE):
            category = "Full Red"
        elif isUpRed(df, position, RATE):
            category = "Up Red"
        elif isDownRed(df, position, RATE):
            category = "Down Red"
        elif df.iloc[position].Short:
            category = "Short Red"
        else:
            category = "Red"
    else:
        if isBalancedDoji(df, position):
            category = "Balanced Doji"
        elif isUpDoji(df, position):
            category = "Up Doji"
        elif isDownDoji(df, position):
            category = "Down Doji"
        else:
            category = "Doji"
    df.Category.iloc[position] = category
