#import libs
from datetime import datetime
import pandas as pd
import sys
#Import binanace API
from binance.client import Client

#add all startegies to importable
sys.path.insert(0, 'engines')

####import modules####
#import Market Engine

#import Entry Engine

#import Risk Engine

#import Exit Engine

#import Stop Engine
from Stops import Stops
#import EMPTY Eninge
from EMPTY import alwaysHold

class DeusNexT:

    State = "BEARISH"

    MarketEngine = None
    EntryEngine = None
    RiskEngine = None
    ExitEngine = None
    StopEngine = None
    
    client = None
    pair = ''
    interval = ''

    lastLossPrice = 0

    def digestCandle(self,candle):

        CurrentStrategy = self.MarketEngine.digestMarket(candle)
        EntrySignal = self.EntryEngine.digestEntry(candle)
        LossPrice, ProfitPrice = self.RiskEngine[CurrentStrategy].digestRisk(candle)
        HasHitStopLoss = self.StopEngine.CheckStopLoss(candle)
        HasHitStopProfit = self.StopEngine.CheckStopProfit(candle)
        ExitSignal = self.ExitEngine[CurrentStrategy].digestExit(candle)

        Signal = ("HOLD",None,None)

        if HasHitStopLoss == False: 

            if HasHitStopProfit:
                print ("-------PROFIT-HIT--------")
                #update stop-loss to breakEven
                self.StopEngine.SetStopLoss(self.lastLossPrice)
                self.StopEngine.SetStopProfit(9999999999)

            #if market is going down
            if self.State == "BEARISH":
                #check for entry Signal
                if EntrySignal == "BUY":
                    Signal = ("BUY", LossPrice, ProfitPrice)
                    self.State = "BULLISH"
            #if market is going up
            elif self.State == "BULLISH":
                #check for exit Signal
                if ExitSignal == "EXIT":
                    Signal = ("SELL",None,None)
                    self.State = "BEARISH"
                elif EntrySignal == "EXIT":
                    Signal = ("SELL",None,None)
                    self.State = "BEARISH"
        #if stop loss was hit 
        else:
            if self.client == None:
                Signal = ("SELL",self.StopEngine.GetStopLoss(),None)
            
            self.StopEngine.SetStopLoss(0.0)
            self.StopEngine.SetStopProfit(9999999999)
            print ("LOSS-HIT")
            self.State = "BEARISH" 

        #returns HOLD, BUY, SELL
        self.lastLossPrice = LossPrice
        return Signal

    def GetStopInstance(self):
        return self.StopEngine


    def initialize(self):

        coinData = self.client.get_historical_klines(symbol= self.pair, interval= self.interval, start_str= "2017.8.20")

        #format data into table of Candles
        Candles = pd.DataFrame(coinData, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])

        Candles["Open"] = Candles["Open"].astype(float)
        Candles["Close"] = Candles["Close"].astype(float)
        Candles["High"] = Candles["High"].astype(float)
        Candles["Low"] = Candles["Low"].astype(float)

        for i,Candle in Candles.iterrows():
            self.digestCandle(Candle)

    def getLastState(self):
        return self.State
    
    
    def __init__(self, _client, _pair, _interval, _TestRun,_stops):

        print ("Initializing DeusNexT")

        self.client = _client
        self.pair = _pair
        self.interval = _interval

        self.MarketEngine = None
        self.EntryEngine = None
        Risk1 = None
        Risk2 = None
        self.RiskEngine = [Risk1,Risk2]
        self.ExitEngine = [alwaysHold(), None]
        self.StopEngine = _stops

        if _TestRun == False:
            self.client = _client
            self.initialize()
            print ("Initialized DeusNexT")
        else:
            return None