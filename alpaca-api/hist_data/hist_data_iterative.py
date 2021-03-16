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


def hist_data(symbol, timeframe="15Min", limit=200, start="", end="", after="", until=""):
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
        
    return temp #df_data



tickers = ["NIO", "PLTR", "AAPL", "AMZN", "FB"]
# time is in seconds 

starttime = time.time()
# will go for 8 hours 
timeout = starttime + 60 * 5 # 8 hrs 60 * 8
while time.time() <= timeout:
    print("****************************************************")
    for company in tickers:
        print("printing data for {} at {}".format(company, time.time()))
        print(hist_data(company, timeframe="5Min"))
        
    # after all ticker, take a break 
    time.sleep(60 - ((time.time() - starttime) % 60)) # the execution of the program will pause (rest)
        

# data_dump = hist_data("NIO,AAPL,PLTR", timeframe="5Min", limit=200)
# print(data_dump)