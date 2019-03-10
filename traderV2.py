import time
import sys
import math
import datetime, getopt
import pandas as pd
from binance.client import Client

#add all startegies to importable

sys.path.insert(0, 'W3CR')
from W3CR import W3CR

class binanceTrader:

    client = None

    pair = ""

    # in "BTCUSDT" quote=USDT base=BTC
    quote = ""
    base = ""

    #binance only handles a given amount of digits, need to rount to that 
    roundTo = 0
    roundToTick = 0
    # each pair has a different stepSize 
    stepSize = 0 

    TickSize = 0

    minQty = 0

    lastOrder = None

    Committer = None


    def checkFounds(self,_price):

            _balance = float(self.client.get_asset_balance(asset = self.base)["free"])

            _quantity = format(round(_balance, self.roundTo) - self.stepSize * 10 , '.6f')

            if float(_quantity) >= float(self.minQty*3):
                print ("----HAS---FUNDS---TO---SELL: "+ str(_quantity))
                return _quantity
            else:
                print ("NOT--ENOUGTH--FUNDS")

    #checks if an order has filled
    def HasFilled(self,_order):

        if _order != None:

            #get order ID
            lastOrderID = _order["orderId"]

            #get information about order
            lastOrder = self.client.get_order(symbol = self.pair, orderId = lastOrderID)

            #from information get status
            lastOrderStatus = lastOrder["status"]

            #if order wasnt Filled
            if lastOrderStatus == "FILLED":
                return True
            else:
                return False
        #if order == None, no order is open   
        else:
            return True


    #cancels last ope order, if filled goes void
    def cancelLastOrder(self):

        #check if order was filled
        Filled = self.HasFilled(self.lastOrder)

        if Filled == False:

            lastOrderID = self.lastOrder["orderId"]

            #get information about order
            lastOrder = self.client.get_order(symbol = self.pair, orderId = lastOrderID)

            try:

                res = self.client.cancel_order(symbol = self.pair, orderId = lastOrderID)

                print ("--CANCELED-----ORDER-----")

            except:

                print ("--NO---OPEN---ORDER---FOUND")

            self.lastOrder = None

        else:

            print ("--ORDER-----FILLED-----")

            self.lastOrder = None

    
    def newStopLoss(self, _stopPrice):

        self.cancelLastOrder()

        _quantity = self.checkFounds(_stopPrice)

        _price = float(_stopPrice)
        _price = round(_price, self.roundToTick)

        try:
            order = self.client.create_order(
                    symbol=self.pair,
                    side="SELL",
                    type="STOP_LOSS_LIMIT",
                    timeInForce = "GTC",
                    quantity=_quantity,
                    price = _price,
                    stopPrice=_price
                )

            print ("----NEW---STOP_SELL---ORDER----")

        except:
            order = None
            print ("----FAILED---TO---MAKE---ORDER----" + str(_quantity) + "  " + str(_price))


        self.lastOrder = order
        return order


        


    def makeTradeBuy(self):

        #get last price and current balance of quote asset
        _price = float(self.client.get_ticker(symbol = self.pair)["lastPrice"])
        _balance = float(self.client.get_asset_balance(asset = self.quote)["free"])

        #round and than subtract to avoid rounding to value higher than balance, margin can be adjusted
        #NOTE: _quantity is amount of base asset to be bought with quote asset
        _quantity =  round(_balance / _price, self.roundTo) - self.stepSize * 2 

        #create order to buy entire balance 
        try: 
            order = self.client.order_limit_buy(
                symbol = self.pair,
                quantity = _quantity,
                price = _price
            )
            #print and return order 
            print ("-----SUCCESSFULLY--PLACED--BUY--ORDER-----")

            #Reveal last Commit and make new Commit with Signal
            self.Committer.Reveal()
            msg = {
                "signal" : "BUY",
                "price" : _price,
            }

            time.sleep(60)
            self.Committer.Commit(msg)


            return order 

        except:
            print ("-----FAILED--TO--MAKE--BUY--ORDER-----")
            time.sleep(1)
            self.makeTradeBuy()


    def makeTradeSell(self):

        self.cancelLastOrder()

        #get last price and current balance of base asset
        _price = float(self.client.get_ticker(symbol = self.pair)["lastPrice"])
        _balance = float(self.client.get_asset_balance(asset = self.base)["free"])

        #round and than subtract to avoid rounding to value higher than balance
        #NOTE: _quantity is amount of base asset to be sold
        _quantity =  round(_balance, self.roundTo) - self.stepSize * 2 

        #create order to sell entire balance 
        try:
            order = self.client.order_limit_sell(
                symbol = self.pair,
                quantity = _quantity,
                price = _price
            )
            #print and return order
            print ("-----SUCCESSFULLY--PLACED--SELL--ORDER-----")

            #Reveal last Commit and make new Commit with Signal
            self.Committer.Reveal()
            msg = {
                "signal" : "SELL",
                "price" : _price,
            }
            time.sleep(60)
            self.Committer.Commit(msg)

            return order 

        except:
            print ("-----FAILED--TO--MAKE--SELL--ORDER-----")
            time.sleep(1)
            self.makeTradeSell()


    
    def tradeSignal(self, _signal):

        #get signal and create orders
        if _signal == "BUY":
            _order = self.makeTradeBuy()

            return _order


        if _signal == "SELL":
            _order = self.makeTradeSell()
            
            return _order


    def __init__(self, _client, _pair, _commiterObject):

        print ("initiating Trader")

        self.pair = _pair
        self.client = _client

        #get stepSize of given pair
        self.stepSize = float(self.client.get_symbol_info(_pair)["filters"][2]["stepSize"])

        #get tickSize of given pair
        self.tickSize = float(self.client.get_symbol_info(_pair)["filters"][0]["tickSize"])

        self.minQty = float(self.client.get_symbol_info(_pair)["filters"][2]["minQty"])

        #get how many digits are supported from stepSize
        for x in range(1,9):
            if self.stepSize == 1.0 / (10 ** x):
                self.roundTo =  x
                break;

        for x in range(1,9):
            if self.tickSize == 1.0 / (10 ** x):
                self.roundToTick =  x
                break;
        
        #get base/quote assets
        self.quote = self.client.get_symbol_info(_pair)["quoteAsset"]
        self.base = self.client.get_symbol_info(_pair)["baseAsset"]


        self.Committer = _commiterObject

        print ("initiated Trader")
