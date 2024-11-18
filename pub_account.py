from bitcoinlib.keys import HDKey
from bitcoinlib.services.services import Service

master_public_file_path = "public"

def list_addresses(k: HDKey, srv: Service):
    for i in range(0, 20):
        search_index(k, srv, str(i))

def search_index(k: HDKey, srv: Service, i: str):
    ck = k.subkey_for_path("0/" + i)

    balance = srv.getbalance(ck.address())
    print("|" + i + "|" + ck.address() + "|" + str(balance/100000000))


if __name__ == "__main__":
    with open(master_public_file_path, 'r') as file:
        xpub_key = file.read()    
    k = HDKey(xpub_key, network="bitcoin")
    srv = Service()
    while True:
        next = input("Please choose next step: [0-list 20 addresses] [1-search by index] [2-exit]")
        if next == "0":
            list_addresses(k, srv)
        elif next == "1":
            index = input("Index:")
            search_index(k, srv, index)
        else:
            exit()