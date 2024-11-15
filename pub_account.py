from bitcoinlib.keys import HDKey
from bitcoinlib.services.services import Service

# add your master public key here
xpub_key = "..."

def search_index(k: HDKey, srv: Service):
    index = input("Index:")
    ck = k.subkey_for_path("0/" + index)
    print("address: " + ck.address())

    balance = srv.getbalance(ck.address())
    print("balance: " + str(balance/100000000))


if __name__ == "__main__":
    k = HDKey(xpub_key, network="bitcoin")
    srv = Service()
    while True:
        next = input("Please choose next step: [0-search] [1-exit]")
        if next == "0":
            search_index(k, srv)
        else:
            exit()