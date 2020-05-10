from rules import *
from configparser import ConfigParser
from icecream import ic
from common import getConfigParser


def getRate():
    parser = getConfigParser()
    return int(parser.get('happy', 'candle_rates'))


def categorizeCandle(df, position):
    categories = []
    RATE = getRate()
    if df.iloc[position].Short:
        df["Categories"][position] = "Short"
        return
    if df.iloc[position].Long:
        categories.append("Long");
    if isRed(df, position):
        categories.append("Red");
    if isUpRed(df, position, RATE):
        categories.append("Up Red");
    if isFullRed(df, position, RATE):
        categories.append("Full Red");
    if isDownRed(df, position, RATE):
        categories.append("Down Red");
    if isGreen(df, position):
        categories.append("Green");
    if isUpGreen(df, position, RATE):
        categories.append("Up Green");
    if isFullGreen(df, position, RATE):
        categories.append("Full Green");
    if isDownGreen(df, position, RATE):
        categories.append("Down Green");
    if isDownDoji(df, position):
        categories.append("Down Doji");
    df["Categories"][position] = "|".join(categories)


def recommendDaily(df, position, stock, portfolio):
    recommendations = [];
    actions = [];
    RATE = getRate()
    c = df.iloc[position];
    p = df.iloc[position + 1];
    # START: Update recommendations for the current day
    # FullGreenCode-I/UpGreenCode-I: Green codes with Increasing trends
    # FullGreenCode-N/UpGreenCode-N: Normal Green codes
    if isLongGreen(df, position):
        recommendations.append("LongGreenCode")
    if isFullGreen(df, position, RATE):
        if isInscreasingTrend(df, position):
            recommendations.append("FullGreenCode-I")
            actions.append("Will Probably Buy")
        else:
            recommendations.append("FullGreenCode-N")
    if isFullRed(df, position, RATE):
        recommendations.append("FullRedCode")
        actions.append("Will Sell");
    if isUpGreen(df, position, RATE):
        if isInscreasingTrend(df, position):
            recommendations.append("UpGreenCode-I")
            actions.append("Will Probably Buy")
        else:
            recommendations.append("FullGreenCode-N")
    if isUpRed(df, position, RATE):
        recommendations.append("UpRedCode")
        actions.append("Will Sell");
    if isDownRed(df, position, RATE):
        recommendations.append("DownRedCode")
        actions.append("Will Sell");
    if isDownDoji(df, position):
        recommendations.append("DownDoji")
        actions.append("Will Sell");
    # Sell when Overcome Profit or Cut Loss
    if isOverProfit(df, position, stock, portfolio):
        # ic("Over Profit")
        recommendations.append("Overcome Profit")
        actions.append("Will Sell");
    
    if isCutLoss(df, position, stock, portfolio):
        # ic("Cut Loss---")
        recommendations.append("Cut Loss")
        actions.append("Will Sell");
    # END: Update recommendations for the current day
    
    # START: Recommend actions based on current day and previous day
    ## BUY is manual check based on current day price: 9 - 10 AM
    ## 1. Current open price is higher that the mean price of the previous day
    ## 2. Current day price has increased higher than the previous high price
    #
    ## SELL: maker sell order from the previous night with open price: 9 - 10 AM
    ## 1. FullRed or DownRed Codes
    ## 2. DownDoji
    ## 3. Previous FullGreen and current FullRed or DownRed
    # if "DownRedCode" in p.Recommendation:
    #     actions.append("Sold")
    # if "FullRedCode" in p.Recommendation:
    #     actions.append("Sold")
    # if "DownDoji" in p.Recommendation:
    #     actions.append("Sold")
    if "Will Sell" in p.Action:
        actions.append("Sold")
        # ic("Sold 1")
    if "UpGreenCode-I" in p.Recommendation:
        # if isFullRed(df, position, RATE) or isUpRed(df, position, RATE): # FullRed or UpRed
        if not (isFullGreen(df, position, RATE) or isDownGreen(df, position, RATE)): # Not FullGreen or DownGreen
            actions.append("Sold");
            # ic("Sold 3")
        elif ("Green" in p.Recommendation) and (not c.Short) and (c.Open > round((p.Close + p.Open)/2)) and (p.High < c.High):
            actions.append("Bought")
            # ic("{} {} {}".format(c.Open, p.Close, p.Open))
            # ic("Bought 1")
    if "FullGreenCode-I" in p.Recommendation:
        # if isFullRed(df, position, RATE) or isUpRed(df, position, RATE): # FullRed or UpRed
        if not (isFullGreen(df, position, RATE) or isDownGreen(df, position, RATE)): # Not FullGreen or DownGreen
            actions.append("Sold");
            # ic("Sold 2")
        else: 
            if c.Short:
                recommendations.append("FullGreenCode-I")
            elif ("Green" in p.Recommendation) and (c.Open > round((p.Close + p.Open)/2)) and (p.High < c.High):
                actions.append("Bought")
                # ic("Bought 2")
    df["Recommendation"][position] = "|".join(recommendations)
    # END: Recommend actions based on current day and previous day

    # START: Set actions
    df.Action.iloc[position] = "|".join(actions)
    # END: Set actions
