import os

import requests
import json
from eth_objects import Block, Transaction, EventLog
from exceptions import *

GETBLOCKIO_KEY = None


def getblock_request(data):
    try:
        headers = {
            'x-api-key': GETBLOCKIO_KEY,
            'Content-Type': 'application/json',
        }
        response = requests.post('https://eth.getblock.io/', headers=headers, data=data)
        if response.status_code != 200:
            if response.status_code == 403 and response.text == "Invalid apikey":
                raise InvalidApiKeyException
            raise FetchDataException("Non-valid status code %d" % response.status_code)
        return json.loads(response.text)["result"]
    except requests.exceptions.RequestException as ex:
        raise FetchDataException("RequestsException")


def get_latest_block_number():
    data = '{ "id": "blockNumber", "jsonrpc": "2.0", "method": "eth_blockNumber", "params": [] }'
    return int(getblock_request(data), base=16)


def get_block_by_number(number):
    data = '{"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["%d", false],"id":1}' % number
    return Block(getblock_request(data))


def bisect(start, end, ts):
    end_block = get_block_by_number(end)
    start_block = get_block_by_number(start)
    mid = int((start + end) / 2)
    mid_block = get_block_by_number(mid)
    if end - start < 10:
        return [start, end]
    elif mid_block.timestamp < ts:
        return bisect(mid, end, ts)
    elif mid_block.timestamp > ts:
        return bisect(start, mid, ts)


def get_block_number_by_ts(ts, n_pre, n_post, last_block=None):
    if last_block is None:
        last_block = get_latest_block_number()

    n_pre = max(1, n_pre)
    n_post = min(n_post, last_block)
    if n_pre == n_post:
        return [n_pre, get_block_by_number(n_pre).timestamp]

    # if block-times were evenly-spaced, get expected block number
    ts_pre, ts_post = get_block_by_number(n_pre).timestamp, get_block_by_number(n_post).timestamp
    av_block_time = (ts_post - ts_pre) / (n_post-n_pre)
    k = (ts - ts_pre) / (ts_post-ts_pre)
    n_expected = int(n_pre + k * (n_post - n_pre))

    # get the ACTUAL time for that block
    ts_expected = get_block_by_number(n_expected).timestamp

    # use the discrepancy to improve the guess
    n_expected_to_target = int((ts - ts_expected) / av_block_time)
    n_expected_adj = n_expected + n_expected_to_target
    r = abs(n_expected_to_target)
    return get_block_number_by_ts(ts, n_expected_adj - r, n_expected_adj + r)


def get_blocks(from_ts, to_ts):
    latest_block_number = get_latest_block_number()
    number_from = bisect(0, latest_block_number, from_ts)[0]
    number_to = bisect(number_from, latest_block_number, to_ts)[1]
    blocks = []
    for i in range(number_from, number_to):
        blocks.append(get_block_by_number(i))
    return blocks


def get_transaction(txn_hash):
    data = '{"jsonrpc":"2.0","method":"eth_getTransactionByHash","params":["%s"],"id":53}' % txn_hash
    return Transaction(getblock_request(data))


def get_transactions(from_ts, to_ts):
    blocks = get_blocks(from_ts, to_ts)
    transactions = []
    for b in blocks:
        print("block hash %s" % b.number)
        for t in b.transactions:
            print("txn hash %s" % t)
            transactions.append(get_transaction(t))
    return transactions


USDT_SMART_CONTRACT_ADDRESS = "0xdac17f958d2ee523a2206206994597c13d831ec7"
USDT_SMART_CONTRACT_TRANSFER_HASH = "ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"


def get_event_logs(from_ts, to_ts, address):
    event_logs = []
    latest_block_number = get_latest_block_number()
    address = int(address, base=16)
    address = "{0:0{1}x}".format(address, 64)
    number_from, ts = get_block_number_by_ts(from_ts, 1, latest_block_number, latest_block_number)
    # skip the found block if its ts is lower than from_ts
    if ts < from_ts:
        number_from += 1
    number_to, ts = get_block_number_by_ts(to_ts, number_from, latest_block_number, latest_block_number)
    # specularly skip the found block if its ts is greater than to_ts
    if ts > to_ts:
        number_to -= 1
    data = '{"jsonrpc":"2.0","method":"eth_getLogs","params":[{"fromBlock":"%s", "toBlock":"%s", "address": "%s", "topics":[["%s"], ["%s"], [null]]}], "id":1}' % (
        number_from, number_to, USDT_SMART_CONTRACT_ADDRESS, USDT_SMART_CONTRACT_TRANSFER_HASH, address)
    logs = getblock_request(data)
    for log in logs:
        event_logs.append(EventLog(log))
    data = '{"jsonrpc":"2.0","method":"eth_getLogs","params":[{"fromBlock":"%s", "toBlock":"%s", "address": "%s", "topics":[["%s"], [null], ["%s"]]}], "id":1}' % (
        number_from, number_to, USDT_SMART_CONTRACT_ADDRESS, USDT_SMART_CONTRACT_TRANSFER_HASH, address)
    logs = getblock_request(data)
    for log in logs:
        event_logs.append(EventLog(log))
    event_logs.sort()
    return event_logs
