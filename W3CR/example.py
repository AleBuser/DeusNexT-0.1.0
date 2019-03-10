from web3 import Web3, HTTPProvider, IPCProvider, WebsocketProvider
from writer import writer
from reader import reader
import hashlib
import json
import time
import sys
from datetime import datetime
from W3CR import W3CR


pkey = None
addr = ''

web3 = Web3(HTTPProvider('https://ropsten.infura.io/v3/--KEY--'))

frst = {
    "signal" : "RESTART",
    "price" : None
}

CR = W3CR(addr,pkey,web3,frst)

count = 0

while True:

    if count < -28:
        break;

    else:
        res = CR.CheckAndGetData(count) 

        if res == None:
            break;

        else:
            print (res) 
            count = count-4








