from bitcoinlib.keys import HDKey
from bitcoinlib.mnemonic import Mnemonic
import aes

seed_file_path = "seed"
master_public_file_path = "public"
hdkey_file_path = "hdkey"
purpose = "84"
coin = "0"
account = "0"
external_internal = "0"
hdkey_detail: str

def start() -> HDKey:
    with open(seed_file_path, 'r') as file:
        content = file.read()

    # test account
    passphrase = input("Passphrase:")

    words = aes.aes256gcm_decode(bytes.fromhex(content), passphrase)

    password = input("the 25th word for seed if have:")

    obj = Mnemonic()
    seed = obj.to_seed(words, password=password).hex()
    k = HDKey.from_seed(seed, key_type="bip32", network="bitcoin", compressed=True, encoding=None, witness_type='segwit', multisig=False)

    # write down master public key
    with open(master_public_file_path, 'w') as file:
        file.write(k.public_master().wif())

    return k


def search_index(k: HDKey):
    index = input("Index:")
    ck = k.subkey_for_path("m/" + purpose + "'/" + coin + "'/" + account + "'/" + external_internal + "/" + index)
    global hdkey_detail
    hdkey_detail = ""
    hdkey_detail += "-----------m/" + purpose + "'/" + coin + "'/" + account + "'/" + external_internal + "/" + index + "-------------------\n"
    hdkey_detail += ck.wif_key() + "\n"
    hdkey_detail += ck.address() + "\n"
    hdkey_detail += ck.public_hex + "\n"
    hdkey_detail += "---------------------------------------------\n"
    print(hdkey_detail)


if __name__ == "__main__":
    k = start()
    while True:
        next = input("Please choose next step: [0-search] [1-export] [2-exit]")
        if next == "0":
            search_index(k)
        elif next == "1":
            with open(hdkey_file_path, 'w') as file:
                file.write(hdkey_detail)
            print("write output to hdkey")           
        else:
            exit()