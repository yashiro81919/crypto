from bitcoinlib.transactions import Transaction

if __name__ == "__main__":
    raw_tx = input("the raw transaction to be verified:")
    t = Transaction.parse(rawtx=raw_tx)
    print(t.verify())