#! /usr/bin/env python
# -*- coding:utf-8 -*-


import time
import json
from websocket import create_connection
import pprint

# pip install websocket-client
ws = ""

def takeAction(action, data):
    if action == "__bet":
        #time.sleep(2)
        ws.send(json.dumps({
            "eventName": "__action",
            "data": {
                "action": "bet",
                "playerName": "CasinoNiBenj",
                "amount": 100
            }
        }))
    elif action == "__action":
        #time.sleep(2)
        ws.send(json.dumps({
            "eventName": "__action",
            "data": {
                "action": "call",
                "playerName": "CasinoNiBenj"
            }
        }))


def doListen():
    try:
        global ws
        ws = create_connection("ws://10.5.60.55:3001/")
        ws.send(json.dumps({
            "eventName": "__join",
            "data": {
                "playerName": "CasinoNiBenj"
            }
        }))
        while 1:
            result = ws.recv()
            msg = json.loads(result)
            event_name = msg["eventName"]
            data = msg["data"]
            print(event_name)
            pprint.pprint(data)
            print(data)
            takeAction(event_name, data)
    except Exception as e:
        print(e)
        ws.close()
        doListen()


if __name__ == '__main__':
    doListen()
