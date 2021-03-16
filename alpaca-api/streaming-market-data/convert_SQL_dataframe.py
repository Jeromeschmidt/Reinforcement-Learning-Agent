import sqlite3
import pandas as pd 


db = sqlite3.connect('')

def get_bars(db, ticker):
    # grabs all data from past 12 days 
    data = pd.read_sql("SELECT * FFROM {} WHERE timestamp >= date() - '12 days'".format("PLTR"), con=db)

    data.set_index(['timestamp'], inplace=True, axis=1)
    # index turns into time
    data.index = pd.to_datetime(data.index)

    # resample data into open, high, low, close every minute
    price_ohlc = data.loc[:, ['price']].resample('1min').ohlc().dropna()
    price_ohlc.columns=["open", "high", "low", "close"]
    vol_ohlc = data.loc[:, ['volume']].resample('1min').apply({'volume':'sum'}).dropna()
    #merge dfs
    df = price_ohlc.merge(vol_ohlc, left_index=True, right_index=True)


get_bars(db, "TSLA") # grab one minute candles from tick db