# -*- coding: utf-8 -*-


import alpaca_trade_api as tradeapi
import os
import json


key = json.loads(open("account.json","r").read())

#creating the API object
api = tradeapi.REST(key["APCA-API-KEY-ID"], key["APCA-API-SECRET-KEY"], base_url='https://paper-api.alpaca.markets')

# api.submit_order("GOOG", 1, "sell", "market", "day")
# api.submit_order("CSCO", 10, "buy", "limit", "day", "44.8")
# api.submit_order("FB", 10, "sell", "stop", "day", stop_price = "271")
# api.submit_order("CSCO", 10, "sell", "trailing_stop", "day", trail_price = "3")


api.close_all_positions()