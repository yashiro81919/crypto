from bitcoinlib.keys import HDKey
from bitcoinlib.mnemonic import Mnemonic
from tronpy.keys import PrivateKey as TronPK
from conf import COIN_CONFIG
import aes, common, questionary

# this script should be deployed on offline device for checking your private key
# make sure a file named "seed" has been put in the same folder which includes the encrypted seed

seed_file_path = "seed"
master_public_file_path = "public"
coin_name: str
hdkey_detail: str

def get_key() -> HDKey:
    password = questionary.password("25th word: ").ask()

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
    index = questionary.text("Index: ", validate=lambda text: len(text) > 0 and common.is_int(text)).ask()
    ck = k.subkey_for_path("m/" + COIN_CONFIG[coin_name]["purpose"] + "'/" + COIN_CONFIG[coin_name]["coin"] + "'/" + COIN_CONFIG[coin_name]["account"] + "'/" + COIN_CONFIG[coin_name]["change"] + "/" + index)
    global hdkey_detail
    hdkey_detail = ""
    hdkey_detail += "-----------m/" + COIN_CONFIG[coin_name]["purpose"] + "'/" + COIN_CONFIG[coin_name]["coin"] + "'/" + COIN_CONFIG[coin_name]["account"] + "'/" + COIN_CONFIG[coin_name]["change"] + "/" + index + "-------------------\n"
    if coin_name in ("BTC", "LTC", "DOGE"):
        hdkey_detail += "WIF: " + ck.wif_key() + "\n"
    hdkey_detail += "Private Key: " + ck.as_hex(private=True).hex() + "\n"
    hdkey_detail += "Public Key: " + ck.as_hex() + "\n"
    if coin_name == "TRX":
        tron_pk = TronPK.fromhex(ck.as_hex(private=True).hex())
        hdkey_detail += "Address: " + tron_pk.public_key.to_base58check_address() + "\n"
    else:
        hdkey_detail += "Address: " + ck.address() + "\n"
    hdkey_detail += "------------------------------------------------\n"
    print(hdkey_detail)


def change_account() -> HDKey:
    global coin_name
    coin_name = common.choose_coin()
    return get_key()


if __name__ == "__main__":
    # load seed file
    with open(seed_file_path, 'r') as file:
        content = file.read()
    
    passphrase = questionary.password("Passphrase: ", validate=lambda text: len(text) > 0).ask()
    words = aes.aes256gcm_decode(bytes.fromhex(content), passphrase)    
    k = change_account()

    action1 = questionary.Choice(title="search", value=0)
    action2 = questionary.Choice(title="change account", value=1)
    action3 = questionary.Choice(title="exit", value=2)    
    while True:
        step = questionary.select("Choose your action: ", choices=[action1, action2, action3]).ask()
        if step == 0:
            search_index(k)
        elif step == 1:
            k = change_account()    
        else:
            exit()