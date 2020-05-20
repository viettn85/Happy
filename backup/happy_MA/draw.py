
from datetime import datetime
import plotly.graph_objects as go
from common import getCsvFiles, readFile

def drawCandlestick(stock):
    
    fig = go.Figure(data=[go.Candlestick(x=dates,
                       open=open_data, high=high_data,
                       low=low_data, close=close_data)])

fig.show()
