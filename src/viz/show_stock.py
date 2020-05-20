from plotly.offline import plot
import plotly.graph_objs as go
import pandas as pd


df = pd.read_csv('/Users/viet_tran/Workplace/Practice/VNStock/d3_data/D2D.csv', parse_dates=True, index_col="Date")
df = df.loc["2020"]

layout = {
    'title': '2019 Feb - 2020 Feb Bitcoin Candlestick Chart',
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
                                            text=df.index.astype(str),
                                            hoverinfo=['text']), 
                            go.Scatter(x=df.index, y=df.MA3, line=dict(color='orange', width=1)),
                            go.Scatter(x=df.index, y=df.MA8, line=dict(color='red', width=1)),
                            go.Scatter(x=df.index, y=df.MA20, line=dict(color='green', width=1))
                      ],
                layout=layout
                )


# fig = dict(data=data, layout=layout)
plot(fig, filename='btc_candles')
