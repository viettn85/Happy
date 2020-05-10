def isRed(df, index):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return c.Open > c.Close;

def isGreen(df, index):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return c.Close > c.Open;

def isFull(high, top, bottom, low, RATE): # Use to check if the canlde stills if full both sides
    return (top - bottom) > RATE * (high - top) and (top - bottom) > RATE * (bottom - low);

def isTopFull(high, top, bottom, low, RATE):
    return (top - bottom) > RATE * (high - top) and (top - bottom) <= RATE * (bottom - low)

def isBottomFull(high, top, bottom, low, RATE):
    return (top - bottom) <= RATE * (high - top) and (top - bottom) > RATE * (bottom - low)

def isLongGreen(df, index):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return c.Close > c.Open and c.Change >= 7

def isFullRed(df, index, RATE):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return isFull(c.High, c.Open, c.Close, c.Low, RATE)

def isFullGreen(df, index, RATE):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return isFull(c.High, c.Close, c.Open, c.Low, RATE)

def isUpRed(df, index, RATE):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return isTopFull(c.High, c.Open, c.Close, c.Low, RATE);

def isUpGreen(df, index, RATE):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return isTopFull(c.High, c.Close, c.Open, c.Low, RATE)

def isDownRed(df, index, RATE):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return isBottomFull(c.High, c.Open, c.Close, c.Low, RATE)

def isDownGreen(df, index, RATE):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return isBottomFull(c.High, c.Close, c.Open, c.Low, RATE)

def isDoji(df, index):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return c.Open == c.Close

def isBalancedDoji(df, index):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return (c.Open == c.Close) and abs(c.High - c.Open) == abs(c.Low - c.Open)

def isUpDoji(df, index):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return (c.Open == c.Close) and (c.High == c.Open)

def isDownDoji(df, index):
    if index >= len(df):
        return False;
    c = df.iloc[index];
    return (c.Open == c.Close) and (c.Low == c.Open)
