# import dependencies
import json
from web3 import Web3
import asyncio
from random import randint
import time
import threading

with open("address.info", "r") as file_obj:
    file_info = file_obj.readlines()

contract_address = file_info[0][:-1]    # there is a \n at the end of the address in address.info
abi = json.loads(file_info[1])

# print(contract_address)
# print()
# print(abi)

ganache_url = 'HTTP://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(ganache_url))
w3.eth.default_account = w3.eth.accounts[0]

evchargingmarket = w3.eth.contract(
    address = contract_address,
    abi = abi
)

# -----------------------------------------MAIN PROGRAM-----------------------------------------
# getting the list of all accounts on the network
accounts_list = w3.eth.get_accounts()

# for account in accounts_list[1:]:
#     print(f"\nUser Info:\nAddress: {account}\nBalance: {evchargingmarket.functions.accounts(account).call()}")

auc_id = 0

print(evchargingmarket.functions.contracts(auc_id).call())
print(evchargingmarket.functions.contracts(auc_id).call()[2])
print(evchargingmarket.functions.contracts(auc_id).call()[1])
print(evchargingmarket.functions.contracts(auc_id).call()[4])
# print(evchargingmarket.functions.getNumBids(auc_id).call())
# print(evchargingmarket.functions.getNumReqs(auc_id).call())

# def handle_event(event):
#     print("\n")
#     print(event['args']['bidder'])
#     print(event['args']['_price'])


# async def log_loop(event_filter, poll_interval):
#     while True:
#         for error in event_filter.get_new_entries():
#             handle_event(error)
#         # time.sleep(2)
#         # thread = threading.Thread(target = open_auction, args = ())
#         # thread.start()
#         await asyncio.sleep(poll_interval)

# event_filter = evchargingmarket.events.BidNotCorrectelyRevealed().createFilter(fromBlock = 'latest')
# loop = asyncio.get_event_loop()
# try:
#     loop.run_until_complete(
#         asyncio.gather(
#             log_loop(event_filter, 2)))
# finally:
#     loop.close()