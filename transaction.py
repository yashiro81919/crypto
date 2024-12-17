from bitcoinlib.transactions import Transaction
from conf import COIN_CONFIG
import common
from bitcash import PrivateKey

# 1. Bitcoin, Litecoin and Dogecoin use the "bitcoinlib"
#    transaction file will be in .bitcoinlib folder in User folder and the name is tx
#    copy this tx file to offline machine to sign the transaction.
# 2. Bitcoin Cash use the "bitcash" and only support send from one address
#    transaction file will be in current folder and the name is tx_bch

tx_file = "tx"
input_addrs = []
output_addrs = []
change_addr = {}
fee_vb: float = 0
total_input: float = 0
total_output: float = 0
total_change: float = 0
fee_str = "-fee"
network: str
witness_type: str
coin_name: str

def print_info():
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


def add_input():
    global total_input
    addr = input("input address:")

    balance = common.get_addr(coin_name, addr)["balance"]/100000000
    total_input += balance

    input_addr = {"address": addr, "balance": str(balance)}
    input_addrs.append(input_addr)   


def add_output():
    global total_output
    global change_addr
    addr = input("output address:")
    balance = input("amount (no value means all available amount):")

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


def create_tx():
    global total_output
    
    t = Transaction(fee_per_kb=fee_vb * 1000, network=network)
    # create input from utxos
    for input_addr in input_addrs:
        utxos = common.get_utxos(coin_name, input_addr["address"])
        for u in utxos:
            t.add_input(prev_txid=u["txid"], output_n=u["output_n"], address=input_addr["address"], value=u["value"], witness_type=witness_type, sequence=4294967293)

    # create output from output_addrs
    for output_addr in output_addrs:
        if fee_str in output_addr["balance"]:
            addOutputWithFee(t, output_addr)
        else:
            t.add_output(get_amount(output_addr), output_addr["address"])
    
    # create output from change_addr if have
    if change_addr != {}:
        addOutputWithFee(t, change_addr)
    
    t.save(filename=tx_file)
    print(t.raw_hex())


def addOutputWithFee(t: Transaction, addr: dict):
    print("transaction size:", t.estimate_size())
    fee = t.calculate_fee()
    print("total fee (sats):", fee)
    amount = get_amount(addr)
    t.add_output(amount - fee, addr["address"])


def create_tx_bch():
    input_addr = input_addrs[0]
    bch_outputs = []
    for output_addr in output_addrs:
        amt = get_amount(output_addr)
        bch_outputs.append((get_cash_addr(output_addr["address"]), amt, "satoshi"))
    leftover = get_cash_addr(change_addr["address"]) if change_addr != {} else None
    tx_data = PrivateKey.prepare_transaction(address=get_cash_addr(input_addr["address"]), outputs=bch_outputs, fee=fee_vb, leftover=leftover)
    with open(tx_file + "_bch", 'w') as file:
        file.write(tx_data)


def get_cash_addr(address: str) -> str:
    if not address.startswith("bitcoincash:"):
        return "bitcoincash:" + address
    return address


def get_amount(addr: dict) -> int:
    if fee_str in addr["balance"]:
        index = addr["balance"].index(fee_str)
        amount = int(round(float(addr["balance"][:index]), 8) * 100000000)
    else:
        amount = int(round(float(addr["balance"]), 8) * 100000000)
    return amount


if __name__ == "__main__":
    coin_name = common.choose_coin()

    network = COIN_CONFIG[coin_name]["network"]
    witness_type = COIN_CONFIG[coin_name]["witness_type"]
    # calculate network fees
    fee_vb = common.get_fee(coin_name)
    print("Current coin is: [" + coin_name + "]")
    while True:
        print_info()
        next = input("Please choose next step: [0]-add input [1]-add output [2]-create transaction [3]-update fee [other]-exit:")
        if next == "0":
            if coin_name == 'BCH' and len(input_addrs) > 0:
                print("Bitcoin Cash only support one input address")
            else:
                add_input()
        elif next == "1":
            add_output()
        elif next == "2":
            # validate input and output
            if len(input_addrs) == 0:
                print("No input address")
            elif len(output_addrs) == 0:
                print("No output address")
            else:       
                if coin_name in ("BTC", "LTC", "DOGE"):
                    create_tx()
                elif coin_name == "BCH":
                    create_tx_bch()
                exit()
        elif next == "3":
            input_fee = input("fee (sat/vB):")
            fee_vb = float(input_fee)
        else:
            exit()