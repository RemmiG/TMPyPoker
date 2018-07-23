#! /usr/bin/env python
# -*- coding:utf-8 -*-

import time
import json
from websocket import create_connection
import pprint
import hashlib

# pip install websocket-client
ws = ""
playerName = "CasinoNiBenj"

def takeAction(action, data, hand, board, chips):
    actionPoint = 5

    if hand[0][0] == 'K':
        hand [0][0] = 13
    elif hand[0][0] == 'Q':
        hand[0][0] = 12
    elif hand[0][0] == 'J':
        hand[0][0] = 11
    elif hand[0][0] == 'A':
        hand[0][0] = 1

    if hand[1][0] == 'K':
        hand [1][0] = 13
    elif hand[1][0] == 'Q':
        hand[1][0] = 12
    elif hand[1][0] == 'J':
        hand[1][0] = 11
    elif hand[1][0] == 'A':
        hand[1][0] = 1

    if (int(hand[0][0]) - int (hand[1][0])) > 3:
        actionPoint -= 2

    elif (int(hand[0][0]) - int (hand[1][0])) == 0:
        actionPoint += 4

    if (hand[0][1] == hand[1][1]):
        actionPoint += 3
    else:
        actionPoint -= 1

    if actionPoint > 7:
        if(chips > 200):
            ws.send(json.dumps({
                "eventName": "__action",
                "data": {
                    "action": "raise",
                    "playerName": playerName,
                    "amount": chips/8
                }
            }))
        else:
            ws.send(json.dumps({
                "eventName": "__action",
                "data": {
                    "action": "allin",
                    "playerName": playerName,
                }
            }))

    if actionPoint >= 4:
        ws.send(json.dumps({
            "eventName": "__action",
            "data": {
                "action": "call",
                "playerName": playerName,
            }
        }))

    if actionPoint < 3:
        ws.send(json.dumps({
            "eventName": "__action",
            "data": {
                "action": "check",
                "playerName": playerName,
            }
        }))
    else:
        ws.send(json.dumps({
            "eventName": "__action",
            "data": {
                "action": "fold",
                "playerName": playerName,
            }
        }))

def doListen():
    try:
        global ws, playerName

        ws = create_connection("ws://10.5.60.55:3001/")
        playerMD5 = hashlib.md5(playerName.encode('utf-8')).hexdigest()

        ws.send(json.dumps({
            "eventName": "__join",
            "data": {
                "playerName": playerName
            }
        }))

        while 1:
            hand = []
            board = []
            chips = 0

            result = ws.recv()
            msg = json.loads(result)
            event_name = msg["eventName"]
            data = msg["data"]

            print(event_name)
            if event_name == "__new_round":
                for p in data["players"]:
                    if p == playerMD5:
                        hand = p["cards"]
                        chips = p["chips"]
                        takeAction(event_name, data, hand, board, chips)


            elif event_name == "__action":
                for p in data["players"]:
                    if p == playerMD5:
                        hand = p["cards"]
                        chips = p["chips"]
                        takeAction(event_name, data, hand, board, chips)


            if event_name == "__deal":
                board = data["table"]["board"]
                takeAction(event_name, data, hand, board, chips)

            pprint.pprint(data)
            print(data)

            
    except Exception as e:
        print(e)
        ws.close()
        doListen()


if __name__ == '__main__':
    doListen()

