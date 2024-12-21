import requests
import json
from conf import COIN_CONFIG

def choose_coin() -> str:
    coins = []
    message = "please choose coin: "
    for index, row in enumerate(COIN_CONFIG):
        message += "[" + str(index) + "]-" + row + " "
        coins.append(row)
    message += ":"
    idx = int(input(message))
    return coins[idx]


def get_utxos(coin_name: str, addr: str) -> list:
    url: str
    response: any
    if coin_name == "BTC":
        url = "https://mempool.space/api/address/" + addr + "/utxo"
        response = json.loads(requests.get(url).text)
    elif coin_name == "LTC":
        url = "https://litecoinspace.org/api/address/" + addr + "/utxo"
        response = json.loads(requests.get(url).text)
    elif coin_name == "DOGE":
        url = "https://api.blockcypher.com/v1/doge/main/addrs/" + addr + "?unspentOnly=1&limit=100"
        tmp = json.loads(requests.get(url).text)
        if "txrefs" in tmp:
            response = tmp["txrefs"]
        else:
            response = []
    elif coin_name == "BCH":
        url = "https://api.fullstack.cash/v5/electrumx/utxos/" + addr
        response = json.loads(requests.get(url).text)["utxos"]
    elif coin_name == "BSV":
        url = "https://api.whatsonchain.com/v1/bsv/main/address/" + addr + "/unspent/all"
        response = json.loads(requests.get(url).text)["result"]

    utxos = []
    for utxo in response:
        if coin_name in ("BTC", "LTC"):
            utxos.append({"txid": utxo["txid"], "output_n": utxo["vout"], "value": utxo["value"]})
        elif coin_name == "DOGE":
            utxos.append({"txid": utxo["tx_hash"], "output_n": utxo["tx_output_n"], "value": utxo["value"]})
        elif coin_name in ("BCH", "BSV"):
            utxos.append({"txid": utxo["tx_hash"], "output_n": utxo["tx_pos"], "value": utxo["value"]})
    return utxos


def get_addr(coin_name: str, addr: str) -> dict:
    url: str
    response: dict
    balance: int
    un_balance: int
    is_spent: bool

    if coin_name in ("BTC", "LTC"):
        url = "https://mempool.space/api/address/" + addr if coin_name == "BTC" else "https://litecoinspace.org/api/address/" + addr
        response = json.loads(requests.get(url).text)
        balance = response["chain_stats"]["funded_txo_sum"] - response["chain_stats"]["spent_txo_sum"]
        un_balance = response["mempool_stats"]["funded_txo_sum"] - response["mempool_stats"]["spent_txo_sum"]
        is_spent = response["chain_stats"]["spent_txo_count"] > 0
    elif coin_name == "DOGE":
        url = "https://api.blockcypher.com/v1/doge/main/addrs/" + addr + "/balance"
        response = json.loads(requests.get(url).text)
        balance = response["balance"]
        un_balance = response["unconfirmed_balance"]
        is_spent = response["total_sent"] > 0
    elif coin_name == "BCH":
        url = "https://api.fullstack.cash/v5/electrumx/balance/" + addr
        response = json.loads(requests.get(url).text)
        balance = response["balance"]["confirmed"]
        un_balance = response["balance"]["unconfirmed"]
        is_spent = False # BCH API don't have this information, so hardcode to False
    elif coin_name == "BSV":
        url = "https://api.whatsonchain.com/v1/bsv/main/address/" + addr + "/confirmed/balance"
        response = json.loads(requests.get(url).text)
        balance = response["confirmed"]
        url1 = "https://api.whatsonchain.com/v1/bsv/main/address/" + addr + "/unconfirmed/balance"
        response1 = json.loads(requests.get(url1).text)
        un_balance = response1["unconfirmed"]
        url2 = "https://api.whatsonchain.com/v1/bsv/main/address/" + addr + "/used"
        response2 = json.loads(requests.get(url2).text)
        is_spent = True if response2 == "true" else False
    return {"balance": balance, "un_balance": un_balance, "is_spent": is_spent}


def get_fee(coin_name: str) -> float:
    url: str
    if coin_name == "BTC":
        url = "https://mempool.space/api/v1/fees/recommended"
    elif coin_name == "LTC":
        url = "https://litecoinspace.org/api/v1/fees/recommended"
    elif coin_name == "DOGE":
        url = "https://api.blockcypher.com/v1/doge/main"
        
    if coin_name in ("BCH", "BSV"):
        return 1 # hard code
    elif coin_name == "DOGE":
        response = json.loads(requests.get(url).text)
        return response['medium_fee_per_kb'] / 1000
    else:
        response = json.loads(requests.get(url).text)
        return response["fastestFee"]
    

def get_raw_tx(coin_name: str, tx_id: str) -> hex:
    if coin_name == "BSV":
        url = "https://api.whatsonchain.com/v1/bsv/main/tx/" + tx_id + "/hex"
        response = requests.get(url).text
        return response   