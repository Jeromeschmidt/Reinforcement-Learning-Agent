import requests
import json as json
from datetime import datetime
import alpaca_trade_api as t
import logging
import pytz
import time

# input : year(date), num of stocks
# output: list of volatile stocks

import yfinance as yf
# from pandas_datareader import data as pdr
import pandas as pd

# list all stocks
url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
df=pd.read_csv(url, sep="|")
print(df.head())
print(df['Symbol'].head())
print(len(df['Symbol']))


def lookup_fn(df, key_row, key_col):
  try:
    return df.iloc[key_row][key_col]
  except IndexError:
    return 0


#get_movement_list
movementlist = []
for stock in df['Symbol']:
  # get history
  thestock = yf.Ticker(stock)
  hist = thestock.history(period="1d") #lookback 1 day
  # print(stock)
  low = float(10000)
  high = float(0)
  # print(thestock.info)
  for day in hist.itertuples(index=True, name='Pandas'):
    if day.Low < low:
      low = day.Low
    if high < day.High:
      high = day.High
  
  deltapercent = 100 * (high - low)/low
  Open = lookup_fn(hist, 0, "Open")
  # some error handling: 
  if len(hist >=5):
    Close = lookup_fn(hist, 4, "Close")
  else :
    Close = Open
  if(Open == 0):
    deltaprice = 0
  else:
    deltaprice = 100 * (Close - Open) / Open #correct zero division error
  print(stock+" "+str(deltapercent)+ " "+ str(deltaprice))
  pair = [stock, deltapercent, deltaprice]
  movementlist.append(pair)

print('here')
#get highest movers (moved morethan 100%)
for entry in movementlist:
  
  if entry[1]>float(100):
    print(entry)  

