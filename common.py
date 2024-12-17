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
        url = "https://bchblockexplorer.com/api/v2/utxo/" + addr
        response = json.loads(requests.get(url).text)
    elif coin_name == "BSV":
        url = "https://api.whatsonchain.com/v1/bsv/main/address/" + addr + "/unspent/all"
        response = json.loads(requests.get(url).text)["result"]

    utxos = []
    for utxo in response:
        if coin_name in ("BTC", "LTC", "BCH"):
            utxos.append({"txid": utxo["txid"], "output_n": utxo["vout"], "value": int(utxo["value"])})
        elif coin_name == "DOGE":
            utxos.append({"txid": utxo["tx_hash"], "output_n": utxo["tx_output_n"], "value": utxo["value"]})
        elif coin_name == "BSV":
            utxos.append({"txid": utxo["tx_hash"], "output_n": utxo["tx_pos"], "value": utxo["value"]})
    return utxos


def get_addr(coin_name: str, addr: str) -> dict:
    url: str
    if coin_name == "BTC":
        url = "https://mempool.space/api/address/" + addr
    elif coin_name == "LTC":
        url = "https://litecoinspace.org/api/address/" + addr
    elif coin_name == "DOGE":
        url = "https://api.blockcypher.com/v1/doge/main/addrs/" + addr + "/balance"
    elif coin_name == "BCH":
        url = "https://bchblockexplorer.com/api/v2/address/" + addr
    elif coin_name == "BSV":
        url = "https://api.whatsonchain.com/v1/bsv/main/address/" + addr + "/confirmed/balance"

    response = json.loads(requests.get(url).text)
    balance: int
    is_spent: bool
    if coin_name in ("BTC", "LTC"):
        balance = response["chain_stats"]["funded_txo_sum"] - response["chain_stats"]["spent_txo_sum"]
        is_spent = response["chain_stats"]["spent_txo_count"] > 0
    elif coin_name == "DOGE":
        balance = response["balance"]
        is_spent = response["total_sent"] > 0
    elif coin_name in ("BCH", "DOGE"):
        balance = int(response["balance"])
        is_spent = int(response["totalSent"]) > 0
    elif coin_name == "BSV":
        balance = response["confirmed"]
        url1 = "https://api.whatsonchain.com/v1/bsv/main/address/" + addr + "/used"
        response1 = json.loads(requests.get(url1).text)
        is_spent = True if response1 == "true" else False
    return {"balance": balance, "is_spent": is_spent}


def get_fee(coin_name: str) -> float:
    url: str
    if coin_name == "BTC":
        url = "https://mempool.space/api/v1/fees/recommended"
    elif coin_name == "LTC":
        url = "https://litecoinspace.org/api/v1/fees/recommended"
    elif coin_name == "DOGE":
        url = "https://api.blockcypher.com/v1/doge/main"
    elif coin_name == "BCH":
        url = "https://bchblockexplorer.com/api/v2/estimatefee/5"
        
    if coin_name == "BSV":
        return 1 # hard code
    elif coin_name == "DOGE":
        response = json.loads(requests.get(url).text)
        return response['medium_fee_per_kb'] / 1000
    elif coin_name == "BCH":
        response = json.loads(requests.get(url).text)
        return float(response["result"]) * 100000
    else:
        response = json.loads(requests.get(url).text)
        return response["fastestFee"]