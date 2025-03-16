from conf import COIN_CONFIG
import common
import json

# 1. Bitcoin, Litecoin and Dogecoin use the "bitcoinlib"
#    transaction file will be in current folder and the name is tx

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


def get_amount(addr: dict) -> int:
    if fee_str in addr["balance"]:
        index = addr["balance"].index(fee_str)
        amount = int(round(float(addr["balance"][:index]), 8) * 100000000)
    else:
        amount = int(round(float(addr["balance"]), 8) * 100000000)
    return amount


if __name__ == "__main__":
    coin_name = common.choose_coin()

    # calculate network fees
    fee_vb = common.get_fee(coin_name)
    print("Current coin is: [" + coin_name + "]")
    while True:
        print_info()
        next = input("Please choose next step: [0]-add input [1]-add output [2]-create transaction [3]-update fee [other]-exit:")
        if next == "0":
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
                create_tx()
                exit()
        elif next == "3":
            input_fee = input("fee (sat/vB):")
            fee_vb = float(input_fee)
        else:
            exit()