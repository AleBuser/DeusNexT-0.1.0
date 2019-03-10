from web3 import Web3, HTTPProvider, IPCProvider, WebsocketProvider
import binascii
class writer():

    pkey = None 
    add = None 
    web3 = None

    def __init__(self, _pkey, _add, _web3):

        self.pkey = _pkey
        self.add = _add
        self.web3 = _web3


    def write(self, _data):

        signed_txn = self.web3.eth.account.signTransaction(dict(
            nonce = self.web3.eth.getTransactionCount(self.add),
            gasPrice = self.web3.eth.gasPrice, 
            gas = 400000,
            to = self.add,
            value = self.web3.toWei(10,'wei'),
            data = _data.encode("utf-8") ,
          ),
          self.pkey)
        txHash = binascii.hexlify(self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)).decode("utf-8")
        return "0x" + str(txHash)