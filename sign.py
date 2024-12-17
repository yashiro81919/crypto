from bitcoinlib.transactions import Transaction
from bitcoinlib.keys import Key
from conf import COIN_CONFIG
import common
from bitcash import Key as CashKey

tx_file = "tx"
signed_tx = "signed_tx"
coin_name: str

def sign():
    network = COIN_CONFIG[coin_name]["network"] 
    witness_type = COIN_CONFIG[coin_name]["witness_type"]

    t = Transaction.load(filename=tx_file)
    t.network = network
    t.witness_type = witness_type

    # loop all input and get all addresses
    addresses = []
    for i in t.inputs:
        addresses.append(i.address)

    # remove duplicate
    new_addresses = list(set(addresses))

    # collect pk and associated to address
    pk_obj = {}
    for idx, address in enumerate(new_addresses):
        pk = input("Please input wif private key for address[" + address + "]:")
        k = Key.from_wif(pk, network=network)
        pk_obj[address] = k
        
    # sign with pk for each input   
    for idx, address in enumerate(addresses):
        k = pk_obj[address]
        t.sign(keys=[k], index_n=idx)

    with open(signed_tx, 'w') as file:
        file.write(t.raw_hex())
        print(t.raw_hex())


def sign_bch():
    with open(tx_file + "_bch", 'r') as file:
        content = file.read()
        
    pk = input("Please input wif private key:")
    key = CashKey(pk)
    tx_hex = key.sign_transaction(content)

    with open(signed_tx, 'w') as file:
        file.write(tx_hex)
        print(tx_hex)


if __name__ == "__main__":
    coin_name = common.choose_coin()
    print("Current coin is: [" + coin_name + "]")

    if coin_name in ("BTC", "LTC", "DOGE"):
        sign()
    elif coin_name == "BCH":
        sign_bch()
