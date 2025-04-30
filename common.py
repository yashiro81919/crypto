from conf import COIN_CONFIG
import requests, json, aes, sqlite3, questionary

def choose_coin() -> str:
    coins = []
    for idx, row in enumerate(COIN_CONFIG):
        coins.append(row)
    coin_name = questionary.select("Choose coin: ", choices=coins).ask()
    print("----------------------------------")
    print("Current coin is: [" + coin_name + "]")
    print("----------------------------------")

    return coin_name


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

    utxos = []
    for utxo in response:
        if coin_name in ("BTC", "LTC"):
            utxos.append({"txid": utxo["txid"], "output_n": utxo["vout"], "value": utxo["value"]})
        elif coin_name == "DOGE":
            utxos.append({"txid": utxo["tx_hash"], "output_n": utxo["tx_output_n"], "value": utxo["value"]})
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
    return {"balance": balance, "un_balance": un_balance, "is_spent": is_spent}


def get_fee(coin_name: str) -> float:
    url: str
    if coin_name == "BTC":
        url = "https://mempool.space/api/v1/fees/recommended"
    elif coin_name == "LTC":
        url = "https://litecoinspace.org/api/v1/fees/recommended"
    elif coin_name == "DOGE":
        url = "https://api.blockcypher.com/v1/doge/main"
        
    if coin_name == "DOGE":
        response = json.loads(requests.get(url).text)
        return response['medium_fee_per_kb'] / 1000
    else:
        response = json.loads(requests.get(url).text)
        return response["fastestFee"]
    

def is_float(text):
    try:
        float(text)
        return True
    except ValueError:
        return False


def is_int(text):
    try:
        int(text)
        return True
    except ValueError:
        return False


def get_api_key(c: sqlite3.Cursor, coin_name: str):
    c.execute("select key from t_key where name = ?", (coin_name,))
    key_row = c.fetchone()
    return aes.aes256gcm_decode(bytes.fromhex(key_row[0]), coin_name).decode('utf-8')     