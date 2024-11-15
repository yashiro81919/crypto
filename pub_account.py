import bitcoinlib

# Replace with your xpub key
xpub_key = "xxxx"

# Create a view-only wallet using the xpub key
wallet = bitcoinlib.wallets.wallet_create_or_open("view_only_wallet5", keys=xpub_key, network="bitcoin", witness_type="segwit", db_uri="sqlite:///bitcoinlib.db")

# Specify the number of addresses to check (e.g., first 10 addresses)
num_addresses = 50
addresses = []

# Retrieve balances and addresses derived from the xpub
print("Checking balance for the first 10 derived addresses:")
for i in range(num_addresses):
    address_info = wallet.key_for_path([0, i])  # Derive the address at index i
    address = address_info.address
    balance = wallet.balance(address_info.key_id)
    addresses.append((address, balance))
    print(f"Address {i}: {address}, Balance: {balance} BTC")

# Optional: Print total balance across all derived addresses
total_balance = sum(balance for _, balance in addresses)
print(f"Total Balance: {total_balance} BTC")