class Stops:

    currentStopLoss = 0 
    currentStopProfit = 999999

    testMode = None

    trader = None


    def CheckStopLoss(self, candle):


        if candle["Low"] <= self.currentStopLoss:
            return True
        else:
            return False



    def CheckStopProfit(self, candle):

        if candle["High"] >= self.currentStopProfit:
            return True
        else:
            return False


    def SetStopLoss(self, price):

        if self.testMode:
            self.currentStopLoss = price
        else:
            self.currentStopLoss = price
            if price != 0.0:
                self.trader.newStopLoss(price)
                print ("")
            else:
                self.currentStopLoss = 0.0
                self.trader.cancelLastOrder()

    def SetStopProfit(self,price):
        self.currentStopProfit = price

    def GetStopLoss(self):
        return self.currentStopLoss


    def GetStopProfit(self):
        return self.currentStopProfit

    def __init__(self, TestRun, traderInstance):

        self.testMode = TestRun

        if not TestRun:
            self.trader = traderInstance