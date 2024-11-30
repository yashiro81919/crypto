from bitcoinlib.transactions import Transaction
from bitcoinlib.keys import Key

tx_file = "tx"

if __name__ == "__main__":
    t = Transaction.load(filename=tx_file)
    t.witness_type = "segwit"

    # loop all input and get the private key
    for idx in range(0, len(t.inputs)):
        pk = input("Please wif private key for input[" + str(idx) + "]:")
        k = Key.from_wif(pk, network="bitcoin")
        t.sign(keys=[k], index_n=idx)

    print("Raw:", t.raw_hex())
    t.info()