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
    df["Categories"][position] = "|".join(categories)


def recommendDaily(df, position):
    recommendations = [];
    RATE = getRate()
    c = df.iloc[position];
    p = df.iloc[position + 1];
    if isLongGreen(df, position):
        recommendations.append("LongGreenCode")
    if isFullGreen(df, position, RATE) and df.iloc[position].Change > 3:
        recommendations.append("FullGreenCode")
    if isFullRed(df, position, RATE):
        recommendations.append("FullRedCode")
        recommendations.append("Sell");
    if isUpGreen(df, position, RATE) and df.iloc[position].Change > 3:
        recommendations.append("UpGreenCode")
    if isDownRed(df, position, RATE):
        recommendations.append("DownRedCode")
        recommendations.append("Sell");
    if "UpGreenCode" in p.Recommendation:
        if ("Red" not in c.Categories) and (not c.Short):
            recommendations.append("Buy")
    if "DownRedCode" in p.Recommendation:
        recommendations.append("Sell")
    if "FullGreenCode" in p.Recommendation:
        if c.Open >= c.Close:
            recommendations.append("Sell");
        else: 
            if c.Short:
                recommendations.append("FullGreenCode")
            else:
                recommendations.append("Buy")

    if "FullRedCode" in p.Recommendation:
        recommendations.append("Sell")
    df["Recommendation"][position] = "|".join(recommendations)
    actions = []
    if "Sell" in recommendations:
        actions.append("Sell")
    if "Buy" in recommendations:
        actions.append("Buy")
    df.Action.iloc[position] = "|".join(actions)