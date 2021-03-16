import websocket 
import os 
import json 


endpoint = "wss://data.alpaca.markets/stream"
headers = json.loads(open("account.json", 'r').read())
streams = ["T.PLTR", "T.NIO", "T.AMZN", "Q.TWTR"]
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
    print(message)

ws = websocket.WebSocketApp("wss://data.alpaca.markets/stream", on_open=on_open, on_message=on_message)

ws.run_forever()