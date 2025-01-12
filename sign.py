from bitcoinlib.transactions import Transaction
from bitcoinlib.keys import Key
from conf import COIN_CONFIG
import common
from bitcash import Key as CashKey
from bsv import Transaction as BSVTrans, PrivateKey, TransactionInput, TransactionOutput, P2PKH
import json

tx_file = "tx"
signed_tx = "signed_tx"
coin_name: str

def sign():
    network = COIN_CONFIG[coin_name]["network"] 
    witness_type = COIN_CONFIG[coin_name]["witness_type"]

    with open(tx_file, 'r') as file:
        content = json.load(file)    

    # loop all input and get all addresses
    addresses = []
    for inp in content["inputs"]:
        addresses.append(inp["address"])

    # remove duplicate
    new_addresses = list(set(addresses))

    # collect pk and associated to address
    pk_obj = {}
    for idx, address in enumerate(new_addresses):
        pk = input("Please input wif private key for address[" + address + "]:")
        k = Key.from_wif(pk, network=network)
        pk_obj[address] = k

    t = Transaction(fee_per_kb=content["fee"] * 1000, network=network, witness_type=witness_type)

    for inp in content["inputs"]:
        t.add_input(prev_txid=inp["txid"], output_n=inp["output_n"], address=inp["address"], value=inp["value"],
            witness_type=witness_type, sequence=4294967293)

    for otp in content["outputs"]:
        if otp["change"]:
            print("transaction size:", t.estimate_size())
            fee = t.calculate_fee()
            print("total fee (sats):", fee)
            t.add_output(otp["amount"] - fee, otp["address"])
        else:
            t.add_output(otp["amount"], otp["address"])   
        
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

    with open(signed_tx + "_bch", 'w') as file:
        file.write(tx_hex)
        print(tx_hex)


def sign_bsv():
    with open(tx_file + "_bsv", 'r') as file:
        content = json.load(file)

    # loop all input and get all addresses
    addresses = []
    for inp in content["inputs"]:
        addresses.append(inp["address"])

    # remove duplicate
    new_addresses = list(set(addresses))

    # collect pk and associated to address
    pk_obj = {}
    for address in new_addresses:
        pk = input("Please input wif private key for address[" + address + "]:")
        k = PrivateKey(pk)
        pk_obj[address] = k          
        
    t = BSVTrans()

    for inp in content["inputs"]:
        t.add_input(TransactionInput(source_transaction=BSVTrans.from_hex(inp["source_tx"]), source_txid=inp["txid"],
            source_output_index=inp["output_n"], unlocking_script_template=P2PKH().unlock(pk_obj[inp["address"]])))

    for otp in content["outputs"]:
        if otp["amount"] != -1:
            t.add_output(TransactionOutput(locking_script=P2PKH().lock(otp["address"]), satoshis=otp["amount"]))
        else:
            t.add_output(TransactionOutput(locking_script=P2PKH().lock(otp["address"]), change=True))

    t.fee(model_or_fee=content["fee"] * 1000)
    t.sign()

    with open(signed_tx + "_bsv", 'w') as file:
        file.write(t.hex())
        print(t.hex())    


if __name__ == "__main__":
    coin_name = common.choose_coin()
    print("Current coin is: [" + coin_name + "]")

    if coin_name in ("BTC", "LTC", "DOGE"):
        sign()
    elif coin_name == "BCH":
        sign_bch()
    elif coin_name == "BSV":
        sign_bsv()
