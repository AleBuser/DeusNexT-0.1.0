import sys
import json
sys.path.insert(0,"/pyethscan")
from etherscan.accounts import Account

class reader():

    add = None 
    web3 = None
    api = None

    def __init__(self, _add, _web3):

        self.add = _add
        self.web3 = _web3

        with open('apiKey.json', mode='r') as key_file:
            key = json.loads(key_file.read())['key']

        self.api = Account(address=_add, api_key=key)


    def read(self, _nr):
        
        transactions = self.api.get_transaction_page(page=1, offset=10000, sort='des')

        return transactions[_nr]


