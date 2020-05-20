from plotly.offline import plot
import plotly.graph_objs as go
import pandas as pd
from identify_candlestick import recognize_candlestick
import sys

stock = str(sys.argv[1])
year = str(sys.argv[2])

df = pd.read_csv('/Users/viet_tran/Workplace/Practice/Happy/data/d3/{}.csv'.format(stock), parse_dates=True, index_col="Date")

df['MA3'] = df.Close.rolling(3).mean()
df['MA5'] = df.Close.rolling(5).mean()
df['MA8'] = df.Close.rolling(8).mean()
df['MA20'] = df.Close.rolling(20).mean()
df['MA120'] = df.Close.rolling(120).mean()
df = df.loc[year]
df = recognize_candlestick(df)
df['3-20'] = df.MA20 - df.MA3
df['3-8'] = df.MA8 - df.MA3
df['8-20'] = df.MA20 - df.MA8

dfTrend = df[['MA3','MA8','MA20','3-8','3-20','8-20']]
dfTrend.to_csv('trends.csv')

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
                            go.Scatter(x=df.index, y=df.MA3, line=dict(color='orange', width=1)),
                            # go.Scatter(x=df.index, y=df.MA5, line=dict(color='black', width=1)),
                            go.Scatter(x=df.index, y=df.MA8, line=dict(color='blue', width=1)),
                            # go.Scatter(x=df.index, y=df.MA20, line=dict(color='green', width=1))
                            # go.Scatter(x=df.index, y=df.MA120, line=dict(color='green', width=1))
                      ],
                layout=layout
                )
plot(fig, filename='vnstock')
