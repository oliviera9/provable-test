import json
from utils import *


class Block:
    def __init__(self, json):
        self.timestamp = int(json["timestamp"], base=16)
        self.number = int(json["number"], base=16)
        self.transactions = json["transactions"]


class Transaction:
    def __init__(self, json):
        self.hash = json["hash"]
        self.hash_from = json["from"]
        self.hash_to = json["to"]


class EventLog:
    def __init__(self, json):
        self.block = int(json["blockNumber"], base=16)
        self.txnHash = json["transactionHash"]
        self.txnIndex = json["transactionIndex"]
        self.data = json["data"]
        self.topics = json["topics"]
        self._json_dict = dict()
        self._json_dict['txid'] = self.txnHash
        self._json_dict['sender'] = eth_topic_to_address(self.topics[1], 40)
        self._json_dict['receiver'] = eth_topic_to_address(self.topics[2], 40)
        self._json_dict['amount'] = int(self.data, base=16) / 1E6

    def __eq__(self, other):
        if self.txnHash == other.txnHash:
            return True
        else:
            return False

    def __ge__(self, other):
        if self.__eq__(other):
            return True
        else:
            if self.block > other.block:
                return True
            elif self.block == other.block:
                if self.txnIndex > other.txnIndex:
                    return True
        return False

    def __lt__(self, other):
        return not self.__ge__(other)

    def to_json(self):
        return json.dumps(self._json_dict)

    def get_dict(self):
        return self._json_dict
