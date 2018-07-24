#! /usr/bin/env python
# -*- coding:utf-8 -*-

import time
import json
from websocket import create_connection
import pprint
import hashlib

# pip install websocket-client
ws = ""
#playerName = "40930"
playerName = "CasinoNiBenj"
#gameServer = "ws://10.104.65.33:3001/"
gameServer = "ws://10.5.60.55:3001"

cardNumber = ['2','3','4','5','6','7','8','9','T','J','Q','K','A']
hand = []
board = []

def checkCards(hand, board):
    currentCards = []
    suiteList = []

    suited = False
    cardSuite = {'D':0,'H':0,'S':0,'C':0}

    for card in hand:
        currentCards.append(card[0])
        suiteList.append(card[1])

    for card in board:
        currentCards.append(card[0])
        suiteList.append(card[1])

    for suite in suiteList:
        for card in cardSuite:
            if(suite == card):
                cardSuite[card] += 1

    for card in cardSuite:
        if len(currentCards) == 2 and cardSuite[card] == 2:
            suited = True
        if cardSuite[card] >= 5:
            suited = True

    calculateOdds(currentCards, suited)

def calculateOdds(currentCards, suited):
    def isConsecutive(cardList):
        cardList = sorted(cardList)
        n = len(cardList)

        minCard = cardList[0]
        maxCard = cardList[n-1]
        
        if (((maxCard - minCard) + 1) == n):
            return True

        return False

    chanceOfWinning = 10
    combinations = {
        "High Card" : 10, #Check/Fold/Bet/Raise
        "Pair" : 9,  #Check/Fold/Bet/Raise
        "Two Pairs" : 8, #Bet/Raise
        "Three of a Kind" : 7, #Bet/Raise
        "Straight" : 6, #Bet/Raise
        "Flush" : 5, #Bet/Raise
        "Full House" : 4, #Raise
        "Four of a Kind" : 3, #All In
        "Straight Flush" : 2, #All In
        "Royal Flush" : 1 #All In
        }

    #Opening Hand
    if(len(currentCards) == 2):
        difference = 0
        goodHand = True

        for card in currentCards:
            difference = abs(difference - cardNumber.index(card))
            if cardNumber.index(card) <= 6:
                goodHand = False

        if difference == 0:
            chanceOfWinning = combinations["Pair"]
            if goodHand:
                takeAction("Raise")
            else:
                takeAction("Call")

        if difference < 3:
            chanceOfWinning = combinations["Straight"]
            if goodHand and suited:
                takeAction("Raise")
            else:
                takeAction("Call")

        if goodHand and suited:
             takeAction("Call")
        elif goodHand or suited:
            takeAction("Check")
        else:
            takeAction("Fold")

        
    else:
        #River
        print(currentCards)
        cardValues = []
        highCard = ''

        for card in currentCards:
            cardValues.append(cardNumber.index(card))

        cardValues = sorted(cardValues)

        highCard = cardValues[len(cardValues)-1]

        pairNumbers = []

        for number in cardNumber:
            count = 0
            for card in currentCards:
                if(number == card):
                    count += 1
            if count > 1:
                pairNumbers.append(count)
                highCard = cardNumber.index(number)

        if len(pairNumbers) > 1:
            if pairNumbers[0] == 3 or pairNumbers[1] == 3:
                chanceOfWinning = combinations["Full House"]
            else:
                chanceOfWinning = combinations["Two Pairs"]
        elif len(pairNumbers) == 1:
            if pairNumbers[0] == 4:
                chanceOfWinning = combinations["Four of a Kind"]
            elif pairNumbers[0] == 3:
                chanceOfWinning = combinations["Three of a Kind"]
            else:
                chanceOfWinning = combinations["Pair"]

        print(pairNumbers)

        straight = isConsecutive(cardValues)

        if straight and len(pairNumbers) == 0:
            chanceOfWinning = combinations["Straight"]

        if suited:
            chanceOfWinning = combinations["Flush"]
            if straight:
                chanceOfWinning = combinations["Straight Flush"]
                if highCard == 'A':
                    chanceOfWinning = combinations["Royal Flush"]

        if chanceOfWinning < 4:
            takeAction("All In")
        elif chanceOfWinning < 7:
            takeAction("Raise")
        elif chanceOfWinning < 9:
            takeAction("Call")
        elif chanceOfWinning == 9 and highCard > 11:
            takeAction("Check")
        else:
            if(len(currentCards) >= 6):
                takeAction("Fold")
            else:
                takeAction("Check")

    print(chanceOfWinning)

def takeAction(actionTaken):
    print("Taking Action!")
    print(actionTaken)

    possibleActions = {
        "All In": "allin",
        "Raise": "raise",
        "Call": "call",
        "Check": "check",
        "Fold": "fold"
    }

    ws.send(json.dumps({
        "eventName": "__action",
        "data": {
            "action": possibleActions[actionTaken],
            "playerName": playerMD5,
        }
    }))

def doListen():
    try:
        global ws, playerName, playerMD5

        ws = create_connection(gameServer)
        playerMD5 = hashlib.md5(playerName.encode('utf-8')).hexdigest()

        ws.send(json.dumps({
            "eventName": "__join",
            "data": {
                "playerName": playerName
            }
        }))

        while 1:
            chips = 0

            result = ws.recv()
            msg = json.loads(result)
            eventName = msg["eventName"]
            data = msg["data"]

            print (eventName)

            if eventName == "__action":
                hand = data["self"]["cards"]
                chips = data["self"]["chips"]
                checkCards(hand, board)

            if eventName == "__bet":
                checkCards(hand, board)

            if eventName == "__deal":
                board = data["table"]["board"]

            if eventName == "__new_round":
                players = data["players"]
                for player in players:
                    if player["playerName"] == playerMD5:
                        hand = player["cards"]
                board = []

            if eventName == "__round_end":
                hand = []
                board = []

    except Exception as e:
        print(e)
        ws.close()
        doListen()


if __name__ == '__main__':
    doListen()