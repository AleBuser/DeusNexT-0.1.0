#Import binanace API
from binance.client import Client
#Import libraries
from datetime import datetime
import time
import pandas as pd
import sys
import math
from web3 import Web3, HTTPProvider, IPCProvider, WebsocketProvider
#add all startegies to importable
sys.path.insert(0, 'strategies')
sys.path.insert(0, 'W3CR')

from DeusNexT import DeusNexT
from traderV2 import binanceTrader
from CandleProvider import dataProvider
from Stops import Stops

from W3CR import W3CR

#Initiate Client connection to Binance
client = Client("KEY", "KEY")

#select trading pair and time from whitch to get data
pair  = "BTCUSDT"
interval  = "1m"

#init the libraries

pkey = 'KEY'
addr = 'KEY'

web3 = Web3(HTTPProvider('https://ropsten.infura.io/v3/KEY'))

frst = {
    "signal" : "RESTART",
    "price" : None
}

CR = W3CR(addr,pkey,web3,frst)

CR.Commit(CR.ToReveal)

Trader = binanceTrader(client, pair, CR)

Stops = Stops(False,Trader)



# last param:  True is Production, True is TEST 
Strategy =DeusNexT(client,pair,interval,False,Stops)

lastState = Strategy.getLastState()

print (lastState)

#last param: return Candles 3 seconds before candele close
Connection = dataProvider(client, pair, interval, 3)


#main loop
while True:

    #check for new candle
    newCandle = Connection.monitorMarket()

    #if a new candle closed
    if(newCandle.empty == False):

        #give new candle to digester to analyze 
        Signal, StopLoss, StopProfit = Strategy.digestCandle(newCandle)

        if int(newCandle["Open"]) % 8 == 0:
            print ("--NOISE--CALL--" + str(int(newCandle["Open"])))

            CR.Reveal()
            msg={
                "signal": "NOISE",
                "price": newCandle["Open"]
            }

            time.sleep(60)
            CR.Commit(msg)

            

        # printa digested Signal and time 
        print ("----------" + Signal + "----------  " + str(datetime.utcnow() ) )

        if Signal == "BUY":
            _buyOrder = Trader.tradeSignal(Signal)

            #wait untill order is filled
            time.sleep(2)
            while Trader.HasFilled(_buyOrder) == False:
                time.sleep(2)
                print ("Wait---For---Fill")
            
            Stops.SetStopLoss(StopLoss)
            Stops.SetStopProfit(StopProfit)

        elif Signal == "SELL":

            if StopLoss == None:
                Trader.tradeSignal(Signal)

            Stops.SetStopProfit(999999999)


    
        


    
