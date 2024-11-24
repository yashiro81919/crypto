from bitcoinlib.transactions import Transaction
from bitcoinlib.services.services import Service

# if srv.sendrawtransaction(t.raw_hex()):
#     print("Transaction send, result: ")
#     print(srv.results)
# else:
#     print("Transaction could not be send, errors: ")
#     print(srv.errors)
transaction_file = "transaction"
input_addrs = []
output_addrs = []
total_input: float = 0
total_output: float = 0

def print_info():
    print("----------------------------------")
    for input_addr in input_addrs:
        print("input addr: " + input_addr["address"] + "|" + str(input_addr["balance"]))
    for output_addr in output_addrs:
        print("output addr: " + output_addr["address"] + "|" + str(output_addr["balance"]))
    print("----------------------------------")


def add_input(srv: Service):
    global total_input
    addr = input("input address:")

    balance = srv.getbalance(addr)/100000000
    total_input += balance

    input_addr = {"address": addr, "balance": balance}
    input_addrs.append(input_addr)   


def add_output():
    global total_output
    addr = input("output address:")
    balance = input("amount:")
    total_output += float(balance)

    output_addr = {"address": addr, "balance": float(balance)}
    output_addrs.append(output_addr)


def create_trans(srv: Service):
    global total_output

    # validate input and output
    if len(input_addrs) == 0:
        print("No input address")
        return False
    elif len(output_addrs) == 0:
        print("No output address")
        return False
    elif total_output >= total_input:
        print("No enough balance to send")
        return False
    
    # calculate network fees
    fee_kb = srv.estimatefee(5) 
    
    t = Transaction(fee_per_kb=fee_kb)
    # create input from utxos
    for input_addr in input_addrs:
        utxos = srv.getutxos(input_addr["address"])
        for u in utxos:
            amount = u["value"]/100000000
            total_output -= amount
            t.add_input(prev_txid=u["txid"], output_n=u["output_n"], compressed=False)
            if total_output <= 0:
                break
    # create output from output_addrs
    for output_addr in output_addrs:
        if total_output == 0 and output_addr == output_addrs[len(output_addrs) - 1]:
            t.add_output(int(round(output_addr["balance"], 8) * 100000000) - t.calculate_fee(), output_addr["address"])
        else:
            t.add_output(int(round(output_addr["balance"], 8) * 100000000), output_addr["address"])
    # send remnant amount back to input address
    if total_output < 0:
        print("Fee per kb:", t.fee_per_kb)
        print("Size:", t.estimate_size())
        fee = t.calculate_fee()
        print("Total fee:", fee)        
        t.add_output(int(round(abs(total_output), 8) * 100000000) - fee, input_addrs[len(input_addrs) - 1]["address"])  
    
    t.save(transaction_file)
    print("Raw:", t.raw_hex())
    return True


if __name__ == "__main__":
    srv = Service(min_providers=10)
    while True:
        print_info()
        next = input("Please choose next step: [0-add input] [1-add output] [2-create transaction] [3-exit]")
        if next == "0":
            add_input(srv)
        elif next == "1":
            add_output()
        elif next == "2":
            if create_trans(srv):
                exit()
        else:
            exit()    