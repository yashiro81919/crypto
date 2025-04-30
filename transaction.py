from tronpy import Tron
from tronpy.providers import HTTPProvider
from conf import TRON_USDT_CONTRACT, DB_FILE
import common, json, questionary, sqlite3

# this script should be deployed on online device for creating transaction data
# transaction file will be in current folder and the name is tx

tx_file = "tx"
input_addrs = []
output_addrs = []
change_addr = {}
fee_vb: float = 0
total_input: float = 0
total_output: float = 0
total_change: float = 0
fee_str = "-fee"
coin_name: str

def get_amount(addr: dict) -> int:
    if fee_str in addr["balance"]:
        index = addr["balance"].index(fee_str)
        amount = int(round(float(addr["balance"][:index]), 8) * 100000000)
    else:
        amount = int(round(float(addr["balance"]), 8) * 100000000)
    return amount


def start():
    global fee_vb
    global total_input
    global total_output
    global change_addr

    # calculate network fees
    fee_vb = common.get_fee(coin_name)

    new_fee = questionary.text("Type new fee if you want to change: ", default=str(fee_vb), validate=lambda text: len(text) > 0 and common.is_float(text)).ask()
    fee_vb = float(new_fee)

    while True:
        addr = questionary.text("Type input address: ", validate=lambda text: len(text) > 0).ask()
        balance = common.get_addr(coin_name, addr)["balance"]/100000000
        total_input += balance   

        input_addr = {"address": addr, "balance": str(balance)}
        input_addrs.append(input_addr)

        status = questionary.confirm("Continue add input address: ").ask()
        if not status:
            break

    while True:
        addr = questionary.text("Type output address: ", validate=lambda text: len(text) > 0).ask()
        balance = questionary.text("Type amount (no value means all available amount): ", validate=lambda text: len(text) == 0 or common.is_float(text)).ask()

        if balance == "":
            balance = str(round(total_input - total_output, 8)) + fee_str
            total_output = total_input
            change_addr = {}
        else:
            total_output += float(balance)
            if (total_output >= total_input):
                print("No enough balance to send")
                total_output -= float(balance)
                return
            else:
                change_addr["address"] = input_addrs[len(input_addrs) - 1]["address"]
                change_addr["balance"] = str(round(total_input - total_output, 8)) + fee_str

        output_addr = {"address": addr, "balance": balance}
        output_addrs.append(output_addr)

        status = questionary.confirm("Continue add output address: ").ask()
        if not status:
            break

    print("----------------------------------")
    print("transaction fee: " + str(fee_vb) + " sat/vB")
    print("----------------------------------")
    for input_addr in input_addrs:
        print("input addr: " + input_addr["address"] + "|" + input_addr["balance"])
    for output_addr in output_addrs:
        print("output addr: " + output_addr["address"] + "|" + output_addr["balance"])
    if change_addr != {}:
        print("change addr: " + change_addr["address"] + "|" + change_addr["balance"])    
    print("----------------------------------")

    status = questionary.confirm("Continue to craete transaction: ").ask()
    if status:   
        tx = {
            "fee": fee_vb,
            "inputs":[],
            "outputs":[]
        }

        # create input from utxos
        for input_addr in input_addrs:
            utxos = common.get_utxos(coin_name, input_addr["address"])
            for u in utxos:
                tx["inputs"].append({"txid": u["txid"], "output_n": u["output_n"], "address": input_addr["address"], "value": u["value"]})

        # create output from output_addrs
        for output_addr in output_addrs:
            if fee_str in output_addr["balance"]:
                tx["outputs"].append({"address": output_addr["address"], "amount": get_amount(output_addr), "change": True})
            else:        
                tx["outputs"].append({"address": output_addr["address"], "amount": get_amount(output_addr), "change": False})

        # create output from change_addr if have
        if change_addr != {}:
            tx["outputs"].append({"address": change_addr["address"], "amount": get_amount(change_addr), "change": True})

        with open(tx_file, 'w') as file:
            file.write(json.dumps(tx))       


def start_trx():
    type = questionary.select("Choose token you want to send: ", choices=["TRX", "USDT"]).ask()
    input_addr = questionary.text("Type input address: ", validate=lambda text: len(text) > 0).ask()
    output_addr = questionary.text("Type output address: ", validate=lambda text: len(text) > 0).ask()
    amt = questionary.text("Type amount you want to send: ", validate=lambda text: len(text) > 0 and common.is_float(text)).ask()
    memo = questionary.text("Any memo if you want: ").ask()

    print("----------------------------------")
    print("Token to be sent: " + type)
    print("From address: " + input_addr)
    print("To address: " + output_addr)
    print("Amount: " + amt)
    print("Memo: " + memo)
    print("----------------------------------")

    status = questionary.confirm("Continue to craete transaction: ").ask()
    if status:
        api_key = common.get_api_key(c, coin_name)
        tron_client = Tron(HTTPProvider(api_key=api_key))

        if type == "TRX":
            tx = tron_client.trx.transfer(input_addr, output_addr, float(amt) * 1_000_000).memo(memo).fee_limit(100_000_000).build()
        elif type == "USDT":
            tron_usdt = tron_client.get_contract(TRON_USDT_CONTRACT)
            tx = tron_usdt.functions.transfer(output_addr, int(float(amt) * 1_000_000)).with_owner(input_addr).fee_limit(5_000_000).build()

        with open(tx_file, 'w') as file:
            file.write(json.dumps(tx.to_json()))


if __name__ == "__main__":
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    coin_name = common.choose_coin()   
    if coin_name == 'TRX':
        start_trx()
    else:
        start()

    c.close()
    conn.close()
    exit()