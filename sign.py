from bitcoinlib.transactions import *
from bitcoinlib.services.services import *

# prev_tx = 'c9124e698d12147616734e473e5a08642283738f516b6d8539dcdb58565a8b91'
# t_i = Input(prev_txid=prev_tx, output_n=1, keys="038d746e10f6db7d95f0d3560bb0c9b3e6ed529fd29ffdbab2cc4b4c232e16b6e8", compressed=False, network="testnet")
# t_o = Output(1000, 'tb1q65kj9xx9kc2lyk6dsdlugj8ak6sd22pgx3q2la', network="testnet")
# t = Transaction([t_i], [t_o])
# t.save("t.file")

t = Transaction()
t.load(filename="t.file")
t.sign(b'Ew\x97\xac9U\xfa\xcf*\xa2R\x1c\xbfK\xcc\x16\xe4t\xc4\xf1\xfc\xdaL6\xb8$\xc3G/F\xfe\x16')
print(t.as_dict())
print("Raw:", t.raw_hex())
print("Verified %s " % t.verify())

srv = Service(network="testnet", min_providers=5)
# r = srv.getutxos("tb1q52nnguyp2x4wrtn30ung2qymxx23wen05tevl9")
# print(r)

# print("\nCurrent estimated networks fees:")
# srv = Service(min_providers=10)
# srv.estimatefee(5)
# print(srv.results)

if srv.sendrawtransaction(t.raw_hex()):
    print("Transaction send, result: ")
    print(srv.results)
else:
    print("Transaction could not be send, errors: ")
    print(srv.errors)