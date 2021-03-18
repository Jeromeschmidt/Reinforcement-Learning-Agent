import requests
import json as json
from datetime import datetime
import alpaca_trade_api as t
import logging
import pandas as pd
import pytz
import time


endpoint = "https://data.alpaca.markets/v1"

headers = json.loads(open("../account.json", 'r').read())


def hist_data(symbol, dataframe, timeframe="15Min", limit=200, start="", end="", after="", until=""):
    '''Returns the historical bar data for a group of stocks '''
    df_data = {}
    # Get Requests for Bar Data
    bar_url = endpoint + "/bars/{}".format(timeframe)

    params = {
        "symbols": symbol,
        "limit": limit,
        "start": start,
        "end": end,
        "after": after,
        "until": until
    }

    r = requests.get(bar_url, headers=headers, params=params)

    json_dump = r.json()
    # loop through stock data
    for symbol in json_dump:
        # convert json into pandas dataframe
        temp = pd.DataFrame(json_dump[symbol])
        temp.rename({"t":"time", "o": "open", 'h':'high', 'l':'low', "c":"close", 'v':'volume'}, axis=1, inplace=True)

        temp = temp.drop(["time", "open", "high", "low", "volume",], axis=1).rename(columns={"close":symbol})
        dataframe = pd.concat([dataframe, temp])

    return dataframe


def getData(tickers):
    dataframes = dict()
    for symbol in tickers:
        dataframes[symbol] = pd.DataFrame(columns = [symbol])

    # time is in seconds

    # starttime = time.time()
    # # will go for 8 hours
    # # timeout = starttime + 60 * 5 # 8 hrs 60 * 8
    # timeout = starttime + 1

    # while time.time() <= timeout:
    print("****************************************************")
    for company in tickers:
        print("printing data for {} at {}".format(company, time.time()))
        dataframes[company] = hist_data(company, dataframes[company], timeframe="5Min")

    final_prices = dataframes[tickers[0]]

    for key, value in dataframes.items():
        final_prices = pd.concat([final_prices, value], axis=1)

    return final_prices

print(getData(["NIO", "PLTR", "AAPL", "AMZN", "FB"]))
