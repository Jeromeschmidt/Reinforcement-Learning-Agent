import requests
import json as json
from datetime import datetime
import alpaca_trade_api as t
import logging
import pandas as pd
import pytz
import time


endpoint = "https://data.alpaca.markets/v1"

headers = json.loads(open("account.json", 'r').read())


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
        temp['time'] = pd.to_datetime(temp['time'], unit='s')
        temp.set_index("time", inplace=True)
        eastern = pytz.timezone('US/Eastern')
        temp.index = temp.index.tz_localize(pytz.utc).tz_convert(eastern)

        # append data to df data
        # df_data[symbol] = temp
        # global df
        # df = pd.concat([df[symbol], temp["close"]])
        # dataframe = pd.concat([dataframe, temp.rename(columns={'close':symbol})[symbol]])
        # dataframe = dataframe.drop([symbol], axis=1)
        # datagrame = dataframe.rename(index={1: symbol})

        # print(dataframe)
        temp = temp.drop(["open", "high", "low", "volume",], axis=1).rename(columns={"close":symbol})
        dataframe = pd.concat([dataframe, temp])
        # print(dataframe)

    # return temp #df_data
    return dataframe



tickers = ["NIO", "PLTR", "AAPL", "AMZN", "FB"]

# df = pd.DataFrame(columns = tickers)
dataframes = dict()
for symbol in tickers:
    dataframes[symbol] = pd.DataFrame(columns = [symbol])

# time is in seconds

starttime = time.time()
# will go for 8 hours
# timeout = starttime + 60 * 5 # 8 hrs 60 * 8
timeout = starttime + 1

while time.time() <= timeout:
    print("****************************************************")
    for company in tickers:
        print("printing data for {} at {}".format(company, time.time()))
        # print(hist_data(company, dataframes[company], timeframe="5Min"))
        dataframes[company] = hist_data(company, dataframes[company], timeframe="5Min")

    # after all ticker, take a break
    # time.sleep(60 - ((time.time() - starttime) % 60)) # the execution of the program will pause (rest)


# data_dump = hist_data("NIO,AAPL,PLTR", timeframe="5Min", limit=200)
# print(data_dump)

final_prices = dataframes[tickers[0]]
print(final_prices[tickers[0]])

for key, value in dataframes.items():
    final_prices = pd.concat([final_prices, value])
    # final_prices = final_prices.join(value, how='outer')

print(final_prices)
