from bitcoinlib.transactions import Transaction
from bitcoinlib.keys import Key

tx_file = "tx"
signed_raw_tx = "raw_tx"

if __name__ == "__main__":
    t = Transaction.load(filename=tx_file)
    t.witness_type = "segwit"

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
        k = Key.from_wif(pk, network="bitcoin")
        pk_obj[address] = k
        
    # sign with pk for each input   
    for idx, address in enumerate(addresses):
        k = pk_obj[address]
        t.sign(keys=[k], index_n=idx)

    print("Raw:", t.raw_hex())
    t.info()
    with open(signed_raw_tx, 'w') as file:
        file.write(signed_raw_tx)
        print("write output to raw_tx")    