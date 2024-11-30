from bitcoinlib.keys import HDKey
from bitcoinlib.services.services import Service
import sqlite3

db_file = "main.db"

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


def choose_account(message: str, rows):
    idx = int(input(message))
    xpub_key = rows[idx][1]
    return (idx, HDKey(xpub_key, network="bitcoin"))      


if __name__ == "__main__":
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("select * from t_account")
    rows = c.fetchall()

    message = "please choose account: "
    for index, row in enumerate(rows):
        message += "[" + str(index) + "]-" + row[0] + " "
    message += ":"

    srv = Service()

    idx, k = choose_account(message, rows)
    while True:
        print("Current account: " + rows[idx][0])
        next = input("Please choose next step: [0]-change account [1]-list 10 addresses [2]-search by index [other]-exit:")
        if next =="0":
            idx, k = choose_account(message, rows)   
        elif next == "1":
            page = input("Page (start from 1):")
            list_addresses(k, srv, page)
        elif next == "2":
            index = input("Index:")
            addr = search_index(k, srv, index)
            get_utxo(srv, addr)
        else:
            c.close()
            conn.close()
            exit()