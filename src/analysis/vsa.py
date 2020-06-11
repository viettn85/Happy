import talib
import statsmodels.api as sm
import pandas as pd

def initialize(context):
    context.security = symbol('AAPL')
    #set_universe(universe.DollarVolumeUniverse(floor_percentile=98.0,ceiling_percentile=100.0))
    
def bar_data(OHLC_type, bars_nr):
    bar_data_func = (history((bars_nr + 1), '1d', OHLC_type).iloc[0]).astype('float')
    return bar_data_func

def handle_data(context, data):
    ######### FEEDING DATA
    # Bar data
    bar_close = 'close_price'
    bar_open = 'open_price'
    bar_high = 'high'
    bar_low = 'low'
    bar_volume = 'volume'
    
    #current_price = data[context.security].price
    price_history = history(bar_count=1, frequency='1d', field='price')
    for s in data:
        current_price = price_history[s][-1]

    ######### ADVANCED DATA
    # Spread data
    yesterday_spread = bar_data(bar_high, 1) - bar_data(bar_low, 1)
    up_bar = bar_data(bar_close, 1) > bar_data(bar_close, 2)
    down_bar = bar_data(bar_close, 1) < bar_data(bar_close, 2)
    
    two_days_ago_spread = bar_data(bar_high, 2) - bar_data(bar_low, 2)
    up_bar_2_bars_ago = bar_data(bar_close, 2) > bar_data(bar_close, 3)
    down_bar_2_bars_ago = bar_data(bar_close, 2) < bar_data(bar_close, 3)

    # Average spread
    last_i_highs = history(30, '1d', 'high')
    last_i_lows = history(30, '1d', 'low')
    average_spread = last_i_highs - last_i_lows
    average_spread = average_spread.mean()

    # Spread factors
    wide_spread_factor = 1.5
    narrow_spread_factor = 0.7
    wide_spread_bar = yesterday_spread > (wide_spread_factor * average_spread)
    wide_spread_bar_2_bars_ago = two_days_ago_spread > (wide_spread_factor * average_spread)
    narrow_spread_bar = yesterday_spread < (narrow_spread_factor * average_spread)
    
    # Bar close range
    bar_range = yesterday_spread / (bar_data(bar_close, 1) - bar_data(bar_low, 1))
    very_high_close_bar = bar_range < 1.35
    high_close_bar = bar_range < 2
    mid_close_bar = (bar_range < 2.2) & (bar_range > 1.8)
    down_close_bar = bar_range > 2

    # Volume data
    volume_history = history(bar_count=100, frequency='1d', field='volume')
    volume_series = volume_history[context.security]
    volume_average = talib.EMA(volume_series, timeperiod=30)

    # Volume moving average
    last_i_volumes = history(30, '1d', 'volume')
    average_volume = last_i_volumes.mean()

    # Trend definition - Linear Regressions
    long_term_history = history(bar_count=40, frequency='1d', field='price')
    medium_term_history = history(bar_count=15, frequency='1d', field='price')
    short_term_history = history(bar_count=5, frequency='1d', field='price')
    
    for S in data:
        long_y = long_term_history[S].values/long_term_history[S].mean()
        long_x = range(len(long_term_history))
        long_a = sm.add_constant(long_x)
        long_results = sm.OLS(long_y, long_a).fit()
        long_interB, long_slopeM = long_results.params
        
        medium_y = medium_term_history[S].values/medium_term_history[S].mean()
        medium_x = range(len(medium_term_history))
        medium_a = sm.add_constant(medium_x)
        medium_results = sm.OLS(medium_y, medium_a).fit()
        medium_interB, medium_slopeM = medium_results.params
        
        short_y = short_term_history[S].values/short_term_history[S].mean()
        short_x = range(len(short_term_history))
        short_a = sm.add_constant(short_x)
        short_results = sm.OLS(short_y, short_a).fit()
        short_interB, short_slopeM = short_results.params
        

    # Returns true if yesterday's volume is lower than the 2 previous days
    two_days_lowest_volume = (bar_data(bar_volume, 1) < bar_data(bar_volume, 2)) & (bar_data(bar_volume, 1) < bar_data(bar_volume, 3))
    
    # Calculate ATR (14)
    atr_highs = history(15, '1d', 'high')
    atr_lows = history(15, '1d', 'low')
    atr_closes = history(15, '1d', 'close_price')
    ATR = pd.DataFrame(index=atr_closes.index,columns=atr_closes.columns)
    for security in list(atr_closes.columns.values):
        ATR[security] = talib.ATR(atr_highs[security],atr_lows[security],atr_closes[security], timeperiod=14)

    # Weakness signal 1
    weakness_signal_1 = wide_spread_bar & down_close_bar & (short_slopeM > 0)
    
    # Strength signal 1
    strength_signal_1 = two_days_lowest_volume & (bar_data(bar_volume, 1) < bar_data(bar_volume, 2)) & (high_close_bar)

    ######### TRADE MANAGEMENT
    position = context.portfolio.positions[context.security].amount
    stop_loss = bar_data(bar_open, 0) - ATR.tail(1)
    take_profit = bar_data(bar_open, 0) + 2*ATR.tail(1)
    stop_loss_hit = bar_data(bar_low, 0) < stop_loss
    take_profit_hit = bar_data(bar_low, 0) > take_profit
    
    if strength_signal_1[0] and (position == 0):
        order_target_percent(context.security, 0.20)
    elif position != 0 or (stop_loss_hit is True) or (take_profit_hit is True):
        order_target_percent(context.security, 0)

print(type(position))
