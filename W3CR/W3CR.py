from web3 import Web3, HTTPProvider, IPCProvider, WebsocketProvider
from writer import writer
from reader import reader
import hashlib
import json
import time
import sys
import random
import string
from datetime import datetime



class W3CR():
    
    Writer = None

    Reader = None

    ToReveal = None

    Address = None

    Password = None

    lastTxHash = None


    def Commit(self, _data):

        key = "".join(random.choices(string.ascii_uppercase, k=9))

        dataToCommit = {
            "data" : _data,
            "key": key,
        }

        dataBytes = json.dumps(dataToCommit)

        self.ToReveal = dataBytes

        Hash = hashlib.sha256(dataBytes.encode()).hexdigest()

        try:
            result = self.Writer.write(Hash)
            print("--COMMIT--")
            self.lastTxHash = result
        except Exception as e:
            result = None
            print ("--WARNING: Failed To Commit--")
            print(e)
            print ("--TRY AGAIN--")
            time.sleep(60)
            self.Commit(_data)
       
        
        return result


    def Reveal(self):

        toReveal = {
            "payload": json.loads(self.ToReveal),
            "commitHash": self.lastTxHash,
        }

        dataBytes = json.dumps(toReveal)
        try:
            self.Writer.write(dataBytes)
            print("--REVEAL--")
        except  Exception as e:
            print ("--WARNING: Failed To Reveal--")
            print(e)
            print ("--TRY AGAIN--")
            time.sleep(60)
            self.Reveal(_data)
        

    def CheckAndGetData(self, _r):

        try:

            Tx = self.Reader.read(_r)

            if Tx != None:

                Proven = False

                if len(Tx["input"]) >135:

                    revealInput = json.loads(self.w3.toText(Tx["input"]))

                    commitTx = self.w3.eth.getTransaction(revealInput["commitHash"])

                    if self.w3.toText(commitTx["input"]) == hashlib.sha256(json.dumps(revealInput["payload"]).encode()).hexdigest():
                        Proven = True

                    ToReturn = {
                        "msg" : revealInput["payload"],
                        "wasCommited" : Proven,
                        "commitmentBlock" : commitTx["blockNumber"] ,
                    }
                    
                    return ToReturn
                else:
                    return "commitTX"

            else:
                return None

        
        except Exception as e:
            print("WARNING: Failed to Read--")
            print(e)
            return None
        


    def __init__(self, _adr, _psw, _w3, _firstRev):

        self.Writer = writer(_psw, _adr, _w3)

        self.w3 = _w3

        self.Reader = reader(_adr, _w3)

        self.Password = _psw

        self.Address = _adr

        self.ToReveal = json.dumps(_firstRev)
