from bitcoinlib.transactions import Transaction
from bitcoinlib.keys import Key
from conf import COIN_CONFIG
import common

tx_file = "tx"
signed_raw_tx = "raw_tx"

if __name__ == "__main__":
    coin_name = common.choose_coin()
    if coin_name == "":
        exit()

    print("Current coin is: [" + coin_name + "]")
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
        pk = input("Please wif private key for address[" + address + "]:")
        k = Key.from_wif(pk, network=network)
        pk_obj[address] = k
        
    # sign with pk for each input   
    for idx, address in enumerate(addresses):
        k = pk_obj[address]
        t.sign(keys=[k], index_n=idx)

    with open(signed_raw_tx, 'w') as file:
        file.write(t.raw_hex())
        print("write output to raw_tx:", t.raw_hex())    