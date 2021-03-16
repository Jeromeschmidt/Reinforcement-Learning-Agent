import websocket 
import os 
import json 
import sqlite3 
import datetime as dt

endpoint = "wss://data.alpaca.markets/stream"
headers = json.loads(open("account.json", 'r').read())
streams = ["T.PLTR", "T.NIO", "T.AMZN", "T.TWTR", "Q.CELH", "Q.SSPK", "T.OPTT"]

# create a database 
db1 = sqlite3.connect('/Users/andrewilliams/Documents/Dev/Alpaca-Api/streaming-market-data/trades_ticks.db')
db2 = sqlite3.connect('/Users/andrewilliams/Documents/Dev/Alpaca-Api/streaming-market-data/quotes_ticks.db')


def return_tickers(streams, tick_type="trades"):
    tickers = []
    if tick_type == 'quotes':
        for symbol in streams:
            tt, ticker = symbol.split(".")
            
            if tt == 'Q' and ticker not in tickers:
                tickers.append(ticker)
                
    elif tick_type == 'quotes':
        for symbol in streams:
            t, ticker = symbol.split(".")
            
            if t == 'T' and ticker not in tickers:
                tickers.append(ticker)
    return tickers
        
def insert_tickers(tick):
    if tick["stream"].split(".")[0] == "T":
        c = db1.cursor()
        for ms in range(100):
            # add a milisecond value to a data timestep
            try:
                table = tick["stream"].split(".")[-1]
                # insert unique time stamps into sql by converting nano seconds to seconds
                vals = [dt.datetime.fromtimestamp(int(tick['data']['t'])/10**9)+dt.timedelta(milliseconds=ms), tick['data']['p'], tick['data']['s']]
                query = "INSERT INTO t{} (timestamp, price, volume) VALUES (?,?,?)".format(table)
                c.execute(query, vals)
                break 
            except Exception as e:
                print(e)
                
        try:
            db1.commit()
        except:
            db1.rollback()
            
    if tick["stream"].split(".")[0] == "Q":
        c = db2.cursor()
        for ms in range(100):
            # add a milisecond value to a data timestep
            try:
                table = tick["stream"].split(".")[-1]
                # insert unique time stamps into sql by converting nano seconds to seconds
                vals = [dt.datetime.fromtimestamp(int(tick['data']['t'])/10**9)+dt.timedelta(milliseconds=ms), tick['data']['p'], tick['data']['P'], tick['data']['s'], tick['data']['S']]
                query = "INSERT INTO q{} (timestamp, bid_price, ask_price, bid_volume, ask_volume) VALUES (?,?,?)".format(table)
                c.execute(query, vals)
                break 
            except Exception as e:
                print(e)
        
        try:
            db2.commit()
        except:
            db2.rollback()
        

def create_tables(db, tickers, tick_type):
    '''Creates db tables from real-time market stream'''
    # to make changes to db 
    c = db.cursor()
    if tick_type == 'trades':
        for ticker in tickers:
            c.execute("CREATE TABLE IF NOT EXISTS t{} (timestamp datetime primary key, price real(15, 5), volume integer)".format(ticker))
    
    elif tick_type == 'quotes':
        for ticker in tickers:
            c.execute("CREATE TABLE IF NOT EXISTS t{} (timestamp datetime primary key, ask_price real(15, 5), bid_price real(15, 5), ask_volume integer, bid_volume integer)".format(ticker))
    try:
        # add to db 
        db.commit()
    # if there's a problem
    except:
        # show any problems w/ change
        db.rollback()

create_tables(db1, return_tickers(streams, "trades"), "trades")
create_tables(db2, return_tickers(streams, "trades"), "trades")
def on_open(ws):
    auth = {
        "action": "authenticate",
        "data": {"key_id":headers['APCA-API-KEY-ID'], "secret_key": headers['APCA-API-SECRET']}
        
    }
    
    ws.send(json.dumps(auth))
    
    message = {
        "action": "listen",
        "data":
            {
                "streams": streams
            }
    }

def on_message(ws, message):
    '''Adds tick data to api '''
    print(message)
    tick = json.loads(message)
    insert_tickers(tick)
    

    

ws = websocket.WebSocketApp("wss://data.alpaca.markets/stream", on_open=on_open, on_message=on_message)

ws.run_forever()