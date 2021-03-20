import requests
import json as json
from datetime import datetime
import alpaca_trade_api as t
import logging
import pytz
import time
import csv
import yfinance as yf
import pandas as pd

def get_stock_symbols():
  sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
  df = sp500[0]
  symbols = df['Symbol'].tolist()
  return symbols

def df_lookup(df, key_row, key_col):
  try:
    return df.iloc[key_row][key_col]
  except IndexError:
    return 0

def get_movement_list(stocks, period):
  movement_list = []
  f = open("stock_changes.csv", "w")
  stock_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
  stock_writer.writerow(["stock", "delta_percent", "delta_price"]) # add header to csv
  for stock in stocks:
    # get history
    curr_stock = yf.Ticker(stock)
    hist = curr_stock.history(period = period) #lookback 1 day

    low = float(10000)
    high = float(0)
    # print(curr_stock.info)
    for day in hist.itertuples(index=True, name='Pandas'):
      if day.Low < low:
        low = day.Low
      if high < day.High:
        high = day.High
    #for zero division error handling
    # if low == 0:
    #   delta_percent = 0
    # else:
    delta_percent = 100 * (high - low) / low #check for division by 0
    Open = df_lookup(hist, 0, "Open")

    # some error handling: 
    if len(hist >= 5):
      Close = df_lookup(hist, 4, "Close")
    else :
      Close = Open

    if (Open == 0):
      delta_price = 0
    else:
      delta_price = 100 * (Close - Open) / Open 
 
    # print(stock+" "+str(delta_percent)+ " "+ str(delta_price))
    pair = [stock, delta_percent, delta_price]
    movement_list.append(pair)
    stock_writer.writerow(pair)
  #close the txt file
  f.close()
  return movement_list 


def get_highest_movers():
  #read the stock_changes csv file
  stocks = pd.read_csv('stock_changes.csv')
  #sort by delta percent
  sorted_stocks = stocks.sort_values('delta_percent', ascending=False)
  # #take the top 20 values
  most_volatile_stocks = sorted_stocks.head(20)
  return most_volatile_stocks['stock'].tolist()

if __name__ == "__main__":
  stocks = get_stock_symbols()
  get_movement_list(stocks, "1d")
  print(get_highest_movers())