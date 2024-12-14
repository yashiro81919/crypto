def choose_coin():
    coin_name: str
    coin_id = input("Please choose coin: [0]-BTC [1]-LTC [2]-DOGE [other]-exit:")
    if coin_id == "0":
        coin_name = "BTC"
    elif coin_id == "1":
        coin_name = "LTC"
    elif coin_id == "2":
        coin_name = "DOGE"
    else:
        coin_name = ""
    return coin_name