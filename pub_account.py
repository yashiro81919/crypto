from bitcoinlib.keys import HDKey
from bitcoinlib.services.services import Service

master_public_file_path = "public"

def list_addresses(k: HDKey, srv: Service, page: str):
    j = int(page)
    for i in range(10 * (j - 1), 10 * j):
        search_index(k, srv, str(i))


def search_index(k: HDKey, srv: Service, i: str):
    ck = k.subkey_for_path("0/" + i)

    balance = srv.getbalance(ck.address())
    print("|" + i + "|" + ck.address() + "|" + str(balance/100000000))
    return ck.address() 


def get_utxo(srv: Service, addr: str):
    utxos = srv.getutxos(addr)
    for u in utxos:
        print(u)


if __name__ == "__main__":
    with open(master_public_file_path, 'r') as file:
        xpub_key = file.read()    
    k = HDKey(xpub_key, network="bitcoin")
    srv = Service()
    while True:
        next = input("Please choose next step: [0-list 10 addresses] [1-search by index] [2-exit]")
        if next == "0":
            page = input("Page (start from 1):")
            list_addresses(k, srv, page)
        elif next == "1":
            index = input("Index:")
            addr = search_index(k, srv, index)
            get_utxo(srv, addr)
        else:
            exit()