# DeusNexT-0.1.0 Alpha

## What it is
DeusNexT is a framework for automating trading strategies, it should allow developers to focus on the implementation and optimization of the trading strategies without needing to worry about the periferical tasks like building testing tools, performance visualization, data formatting ecc.

### Back-Testing
The DNT framework currently offers tools to combine different indicators into a complete trading startegy, this strategy can be tested on all timeframes and currency pairs, the testing returns a set of performance statistics such as net-profit, highest gain, drawdown, Win/Loss ratio, ecc. as well as a graph showing Strategy performance compared to assed price, and Trade-Profit Histograms.

During the tesing the Strategy is fed with consecutive candles the same way the real on market execution will do, allowing for percise simulations of real conditions.

### Deploying
When enough testing is done the strategy can be deployed to the market, for this DNT offers the tools to get the formated candles form the Exchange, push the candles into the startegy and execute trades based on the signals provided by the Strategy

![DNT Architecture](https://github.com/AleBuser/DeusNexT-0.1.0/blob/master/DNT-Architecture.jpg)

## How to get Started
To get started implementing your own trading startegy download the code and write the indicators you want to use for the different engines of the startegy, save these files in the engines folder and import them into the Strategy.py file. 
You can now run the testRun.py script to mesure the performance of your strategy!

### Return values:
In ordert o be compatible with the rest of the code your engines need to return the right values, these are:
```
MarketEngine -> returns the integer value of the array-index of the startegy to be used for the current candle
```
```
EntryEngine -> returns either "BUY" or "HOLD"
```
```
RiskEngine -> returns 2 price levels at witch to place the StopLoss an StopProfit for the given candle
```
```
ExitEngine -> returns either "EXIT" or "HOLD"
```

## TO-DO
-Currently the Trader.py only supports StopLoss, TODO: implementing a StopProfit to take partial profits

-Currently the Trader.py only supports Market Orders, TODO: implementing the option for LimitOrders

-Other cool stuff
