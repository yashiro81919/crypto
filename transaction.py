from bitcoinlib.transactions import Transaction
from conf import COIN_CONFIG
import common

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


def create_trans():
    global total_output

    # validate input and output
    if len(input_addrs) == 0:
        print("No input address")
        return False
    elif len(output_addrs) == 0:
        print("No output address")
        return False
    
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
            t.add_output(int(round(float(output_addr["balance"]), 8) * 100000000), output_addr["address"])
    
    # create output from change_addr if have
    if change_addr != {}:
        addOutputWithFee(t, change_addr)
    
    t.save(filename=tx_file)
    print(t.raw_hex())
    return True


def addOutputWithFee(t: Transaction, addr):
    print("transaction size:", t.estimate_size())
    fee = t.calculate_fee()
    print("total fee (sats):", fee)
    index = addr["balance"].index(fee_str)
    amount = int(round(float(addr["balance"][:index]), 8) * 100000000)
    t.add_output(amount - fee, addr["address"])     


if __name__ == "__main__":
    coin_name = common.choose_coin()
    if coin_name == "":
        exit()

    network = COIN_CONFIG[coin_name]["network"]
    witness_type = COIN_CONFIG[coin_name]["witness_type"]
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
            if create_trans():
                exit()
        elif next == "3":
            input_fee = input("fee (sat/vB):")
            fee_vb = float(input_fee)
        else:
            exit()