from bitcoinlib.keys import HDKey
from bitcoinlib.mnemonic import Mnemonic
import aes
from conf import COIN_CONFIG
import common

seed_file_path = "seed"
master_public_file_path = "public"
coin_name: str
hdkey_detail: str
words: str

def get_key() -> HDKey:
    password = input("the 25th word for seed if have:")

    obj = Mnemonic()
    seed = obj.to_seed(words, password=password).hex()
    network = COIN_CONFIG[coin_name]["network"]
    witness_type = COIN_CONFIG[coin_name]["witness_type"]
    k = HDKey.from_seed(seed, network=network, compressed=True, encoding=None, witness_type=witness_type, multisig=False)

    pub = k.subkey_for_path("m/" + COIN_CONFIG[coin_name]["purpose"] + "'/" + COIN_CONFIG[coin_name]["coin"] + "'/" + COIN_CONFIG[coin_name]["account"] + "'").public()
    # write down master public key
    with open(master_public_file_path, 'w') as file:
        file.write(pub.wif())

    return k


def search_index(k: HDKey):
    index = input("Index:")
    ck = k.subkey_for_path("m/" + COIN_CONFIG[coin_name]["purpose"] + "'/" + COIN_CONFIG[coin_name]["coin"] + "'/" + COIN_CONFIG[coin_name]["account"] + "'/" + COIN_CONFIG[coin_name]["change"] + "/" + index)
    global hdkey_detail
    hdkey_detail = ""
    hdkey_detail += "-----------m/" + COIN_CONFIG[coin_name]["purpose"] + "'/" + COIN_CONFIG[coin_name]["coin"] + "'/" + COIN_CONFIG[coin_name]["account"] + "'/" + COIN_CONFIG[coin_name]["change"] + "/" + index + "-------------------\n"
    hdkey_detail += ck.wif_key() + "\n"
    hdkey_detail += ck.address() + "\n"
    hdkey_detail += ck.public_hex + "\n"
    hdkey_detail += "---------------------------------------------\n"
    print(hdkey_detail)


def change_account() -> HDKey:
    global coin_name
    coin_name = common.choose_coin()
    print("Current coin is: [" + coin_name + "]")
    return get_key()


if __name__ == "__main__":
    # load seed file
    with open(seed_file_path, 'r') as file:
        content = file.read()
    passphrase = input("Passphrase:")
    words = aes.aes256gcm_decode(bytes.fromhex(content), passphrase)    
    k = change_account()
    while True:
        next = input("Please choose next step: [0]-change account [1]-search [other]-exit:")
        if next == "0":
            k = change_account()
        elif next == "1":
            search_index(k)          
        else:
            exit()