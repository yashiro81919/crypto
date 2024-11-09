from bitcoinlib.keys import HDKey
from bitcoinlib.mnemonic import Mnemonic
import aes

seed_file_path = "seed"
master_public_file_path = "public"
purpose = "84"
coin = "0"
account = "0"
external_internal = "0"

with open(seed_file_path, 'r') as file:
    content = file.read()

# test account
passphrase = input("Passphrase:")
password = input("the 25th word for seed if have:")

words = aes.aes256gcm_decode(bytes.fromhex(content), passphrase)

obj = Mnemonic()
seed = obj.to_seed(words, password=password).hex()
k = HDKey.from_seed(seed, key_type="bip32", network="bitcoin", compressed=True, encoding=None, witness_type='segwit', multisig=False)

# write down master public key
with open(master_public_file_path, 'w') as file:
    file.write(k.public_master().wif())

index = input("Index:")
ck = k.subkey_for_path("m/" + purpose + "'/" + coin + "'/" + account + "'/" + external_internal + "/" + index)
print("-----------m/" + purpose + "'/" + coin + "'/" + account + "'/" + external_internal + "/" + index + "-------------------")
print(ck.wif_key())
print(ck.address())
print(ck.public_hex)
print(ck.private_byte)
print("---------------------------")