from bitcoinlib.keys import HDKey
from conf import COIN_CONFIG, DB_FILE
import sqlite3, common, questionary

# this script should be deployed on online device for monitoring your accounts
# accounts are saved in table t_account

coin_name: str
account = 0 # always use this 0
account_name: str
total: float

def list_addresses(k: HDKey):
    global total
    total = 0
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
    if show_non_zero:
        global total
        total += balance
        
    if not show_non_zero or (balance + un_balance) > 0:
        is_spent = "✘" if addr["is_spent"] else "✔"
        address = ck.address()
        print("|" + i + "|" + address + "|" + str(balance) + "|" + is_spent)

    if show_utxo:
        utxos = common.get_utxos(coin_name, ck.address())
        for u in utxos:
            print(u)

    update_db(i, balance + un_balance)


def choose_account(db_accounts: list[questionary.Choice], rows: list[any]) -> tuple:
    global coin_name
    
    idx = questionary.select("Choose account: ", choices=db_accounts).ask()
    xpub_key = rows[idx][1]
    coin_name = rows[idx][2]
    network = COIN_CONFIG[coin_name]["network"]
    witness_type = COIN_CONFIG[coin_name]["witness_type"]

    return (idx, HDKey(xpub_key, network=network, witness_type=witness_type))      


def update_db(i: str, value: float):
    c.execute("select count(*) from t_address where name = ? and idx = ?", (account_name, int(i)))
    addr_row = c.fetchone()
    if addr_row[0] == 0 and value > 0:
        c.execute("insert into t_address (name, idx) values (?, ?)", (account_name, int(i)))
        conn.commit()
    elif addr_row[0] > 0 and value == 0:
        c.execute("delete from t_address where name = ? and idx = ?", (account_name, int(i)))
        conn.commit()     


if __name__ == "__main__":
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("select * from t_account")
    rows = c.fetchall()

    db_accounts = []
    for idx, row in enumerate(rows):
        db_accounts.append(questionary.Choice(title=row[0], value=idx))

    idx, k = choose_account(db_accounts, rows)
    while True:
        account_name = rows[idx][0]
        print("----------------------------------")
        print("Current account is: [" + account_name + "]")
        print("----------------------------------")

        action1 = questionary.Choice(title="list using addresses", value=0)
        action2 = questionary.Choice(title="search by index", value=1)
        action3 = questionary.Choice(title="change account", value=2)        
        action4 = questionary.Choice(title="exit", value=3)     
        step = questionary.select("Choose your action: ", choices=[action1, action2, action3, action4]).ask()   
        if step == 0:
            list_addresses(k)   
        elif step == 1:
            index = questionary.text("Index: ", validate=lambda text: len(text) > 0 and common.is_int(text)).ask()
            search_index(k, index, False, True)
        elif step == 2:
            idx, k = choose_account(db_accounts, rows)
        else:
            c.close()
            conn.close()
            exit()