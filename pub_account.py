from bitcoinlib.keys import HDKey
import sqlite3
from conf import COIN_CONFIG
import common

db_file = "acc.db"
coin_name: str
account = 0 # always use this 0
account_name: str
total = 0

def list_addresses(k: HDKey):
    c.execute("select * from t_address where name = ?", (account_name,))
    using_addrs = c.fetchall()
    for using_addr in using_addrs:
        search_index(k, str(using_addr[1]), True, False)
    print('Total Balance:' + str(total))


def search_index(k: HDKey, i: str, show_non_zero: bool, show_utxo: bool):
    ck = k.subkey_for_path(str(account) + "/" + i)

    # fetch balance
    addr = common.get_addr(coin_name, ck.address())
    balance = addr["balance"]/100000000
    un_balance = addr["un_balance"]/100000000

    # calculate total balance
    global total
    total += balance

    # update db
    c.execute("select count(*) from t_address where name = ? and idx = ?", (account_name, int(i)))
    addr_row = c.fetchone()
    if addr_row[0] == 0 and (balance + un_balance) > 0:
        c.execute("insert into t_address (name, idx) values (?, ?)", (account_name, int(i)))
        conn.commit()
    elif addr_row[0] > 0 and (balance + un_balance) == 0:
        c.execute("delete from t_address where name = ? and idx = ?", (account_name, int(i)))
        conn.commit() 
        
    if not show_non_zero or (balance + un_balance) > 0:
        is_spent = "✘" if addr["is_spent"] else "✔"
        address = ck.address()
        print("|" + i + "|" + address + "|" + str(balance) + "|" + is_spent)

    if show_utxo:
        utxos = common.get_utxos(coin_name, ck.address())
        for u in utxos:
            print(u)


def choose_account(message: str, rows) -> tuple:
    global coin_name
    
    idx = int(input(message))
    xpub_key = rows[idx][1]
    coin_name = rows[idx][2]
    network = COIN_CONFIG[coin_name]["network"]
    witness_type = COIN_CONFIG[coin_name]["witness_type"]
    return (idx, HDKey(xpub_key, network=network, witness_type=witness_type))      


if __name__ == "__main__":
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("select * from t_account")
    rows = c.fetchall()

    message = "please choose account: "
    for index, row in enumerate(rows):
        message += "[" + str(index) + "]-" + row[0] + " "
    message += ":"

    idx, k = choose_account(message, rows)
    while True:
        account_name = rows[idx][0]
        print("Current account: " + account_name)
        next = input("Please choose next step: [0]-change account [1]-list using addresses [2]-search by index [other]-exit:")
        if next =="0":
            idx, k = choose_account(message, rows)   
        elif next == "1":
            list_addresses(k)
        elif next == "2":
            index = input("Index:")
            search_index(k, index, False, True)
        else:
            c.close()
            conn.close()
            exit()