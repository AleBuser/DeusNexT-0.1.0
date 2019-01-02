#Import binanace API
from binance.client import Client
#Import libraries
from datetime import datetime
import time
import pandas as pd
import sys

#add all engines to importable
sys.path.insert(0, 'engines')

### import modules ###
from Strategy import Strategy
from Trader import binanceTrader
from CandleProvider import dataProvider
from Stops import Stops
######################

#Initiate Client connection to Binance
client = Client("KEY", "KEY")

#select trading pair and time from whitch to get data
pair  = "BTCUSDT"
interval  = "1h"

#init the modules
Trader = binanceTrader(client, pair)
Stops = Stops(TestRun = False, traderInstance = Trader)

# init Startegy
Strategy = Strategy(client, pair, interval, TestRun = False, StopsEngineInstance = Stops)
# get initial state of strategy
lastState = Strategy.getLastState()
#print State
print lastState

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

        # printa digested Signal and time 
        print "----------" + Signal + "----------  " + str(datetime.utcnow() ) 

        #wants to buy
        if Signal == "BUY":

            #Create Order
            _buyOrder = Trader.tradeSignal(Signal)

            #wait untill order is filled
            while Trader.HasFilled(_buyOrder) == False:
                time.sleep(2)
            
            #put in Stops
            Stops.SetStopLoss(StopLoss)
            Stops.SetStopProfit(StopProfit)

        #wants to sell
        elif Signal == "SELL":

            #Create Order 
            if StopLoss == None:
                Trader.tradeSignal(Signal)

            #reset Stop
            Stops.SetStopProfit(999999999)

    
        


    
