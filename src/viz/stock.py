from plotly.offline import plot
import plotly.graph_objs as go
import pandas as pd
from identify_candlestick import recognize_candlestick
import sys

stock = str(sys.argv[2])
year = str(sys.argv[1])

if len(sys.argv) > 3:
    df = pd.read_csv('/Users/viet_tran/Workplace/Practice/Happy/data/all/{}.csv'.format(stock), parse_dates=True, index_col="Date")
else:
    df = pd.read_csv('/Users/viet_tran/Workplace/Practice/Happy/data/daily/{}.csv'.format(stock), parse_dates=True, index_col="Date")
df.sort_index(ascending=True, inplace=True)

df['Mean'] = df.Close/2 + df.Open/2
df['MA3_Open'] = df.Open.rolling(3).mean()
df['MA3_Close'] = df.Close.rolling(3).mean()
df['MA8_Open'] = df.Open.rolling(8).mean()
df['MA8_Close'] = df.Close.rolling(8).mean()
df = df.loc['2019':year]
df = recognize_candlestick(df)
df['3-20'] = df.MA20 - df.MA3
df['3-8'] = df.MA8 - df.MA3
df['8-20'] = df.MA20 - df.MA8


layout = {
    'title': '{} - {}'.format(stock, year),
    'yaxis': {'title': 'Price'},
    'xaxis': {'title': 'Index Number'},

}
# plot the candlesticks
fig = go.Figure(data = [
                            go.Candlestick( x=df.index,
                                            open=df.Open, 
                                            high=df.High,
                                            low=df.Low,
                                            close=df.Close,
                                            text=df.index.astype(str) + ' ' + df.candlestick_pattern.astype(str),
                                            hoverinfo=['text']), 
                            go.Scatter(x=df.index, y=df.MA3_Close, line=dict(color='orange', width=1)),
                            go.Scatter(x=df.index, y=df.MA8_Close, line=dict(color='blue', width=1)),
                            go.Scatter(x=df.index, y=df.MA3_Open, line=dict(color='red', width=1)),
                            # go.Scatter(x=df.index, y=df.MA20, line=dict(color='green', width=1)),
                      ],
                layout=layout
                )
plot(fig, filename='vnstock.html')
