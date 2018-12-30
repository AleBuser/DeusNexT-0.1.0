#import libs
from datetime import datetime
import pandas as pd
import sys
#Import binanace API
from binance.client import Client

#add all startegies to importable
sys.path.insert(0, 'engines')



####import modules####
#import Market Engines

#import Entry Engines


#import Risk Engines


#import Exit Engines


#import Stop Engines


#import EMPTY Exit Eninge
from EMPTY import alwaysHold

######################



class Strategy:

    State = "BEARISH"

    #engine instances
    MarketEngine = None
    EntryEngine = None
    RiskEngine = None
    ExitEngine = None
    StopEngine = None
    
    #binance info for initialization
    client = None
    pair = ''
    interval = ''



    def digestCandle(self,candle):

        #pass candle through every engine to get its result

        #gets strategy ID to use
        CurrentStrategyID = self.MarketEngine.digestMarket(candle)
        #gets EntrySignal = "BUY" or "HOLD"
        EntrySignal = self.EntryEngine.digestEntry(candle)
        #gets 2 price levels
        LossPrice, ProfitPrice = self.RiskEngine[CurrentStrategyID].digestRisk(candle)
        #gets a boolean
        HasHitStopLoss = self.StopEngine.CheckStopLoss(candle)
        #gets a boolean
        HasHitStopProfit = self.StopEngine.CheckStopProfit(candle)
        #gets ExitSignal = "EXIT" or "HOLD"
        ExitSignal = self.ExitEngine[CurrentStrategyID].digestExit(candle)

        #initialize signal Tuple
        Signal = ("HOLD",None,None)

        #check for stop hit
        if HasHitStopLoss == False: 

            if HasHitStopProfit:
                print "-------PROFIT-HIT--------"
                #update stop-loss to breakEven
                self.StopEngine.SetStopLoss(LossPrice)
                self.StopEngine.SetStopProfit(9999999999)

            #if market is going down
            if self.State == "BEARISH":
                #check for entry Signal
                if EntrySignal == "BUY":
                    #generate signal with stop levels
                    Signal = ("BUY", LossPrice, ProfitPrice)
                    self.State = "BULLISH"
            #if market is going up
            elif self.State == "BULLISH":
                #check for exit Signal
                if ExitSignal == "EXIT" or EntrySignal == "EXIT":
                    #generate signal
                    Signal = ("SELL",None,None)
                    self.State = "BEARISH"
        #if stop loss was hit 
        else:
            #if in test mode
            if self.client == None:
                Signal = ("SELL",self.StopEngine.GetStopLoss(),None)

            #reset Stops
            self.StopEngine.SetStopLoss(0.0)
            self.StopEngine.SetStopProfit(9999999999)
            print "LOSS-HIT"
            self.State = "BEARISH" 

        #returns HOLD, BUY, SELL
        return Signal

    #in production the indicators need to be initialized with historical data
    def initialize(self):

        coinData = self.client.get_historical_klines(symbol= self.pair, interval= self.interval, start_str= "2018.12.20")

        #format data into table of Candles
        Candles = pd.DataFrame(coinData, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])

        Candles["Open"] = Candles["Open"].astype(float)
        Candles["Close"] = Candles["Close"].astype(float)
        Candles["High"] = Candles["High"].astype(float)
        Candles["Low"] = Candles["Low"].astype(float)

        #use historical data to derive current state
        for i,Candle in Candles.iterrows():
            self.digestCandle(Candle)

    #returns current state = "BULLISH" or "BEARISH"
    def getLastState(self):
        return self.State



    

    def __init__(self, _client, _pair, _interval, TestRun, StopsEngineInstance):

        print "Initializing DeusNexT"

        #store Binance data
        self.client = _client
        self.pair = _pair
        self.interval = _interval

        #self.MarketEngine = MarketStrategy
        #self.EntryEngine = [EntryStrategy1, EntryStrategy2]
        #self.RiskEngine = [RiskStartegy1, RiskStrategy2]
        #self.ExitEngine = [ExitStrategy1, ExitStrategy2]
        self.StopEngine = StopsEngineInstance

        #if test initialize 
        if TestRun == False:
            self.client = _client
            self.initialize()
            print "Initialized DeusNexT"
        else:
            return None