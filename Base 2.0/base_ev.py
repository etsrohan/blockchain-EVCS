from web3 import Web3
import json
import time
import asyncio
from random import randint

with open("address.info", "r") as file_obj:
	file_info = file_obj.readlines()

contract_address = file_info[0][:-1]	# there is a \n at the end of the address in address.info
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

# testing to see if contract connected properly
# print(evchargingmarket.functions.getNumberOfReq().call())

# getting the list of all accounts on the network
accounts_list = w3.eth.get_accounts()

# separating the EV addresses 2/3rd of the networks
separator = int((len(w3.eth.get_accounts()) - 1) / 3) + 1
EV_addresses = accounts_list[separator : ]

while True:
    for addr in EV_addresses:
        # lets try to create a charging request by user
        request_id = evchargingmarket.functions.getNumberOfReq().call()
        w3.eth.default_account = addr
        auction_time = 30

        tx_hash = evchargingmarket.functions.createReq(100, 10, int(time.time()) + auction_time, auction_time, 5).transact()	# Random values for now to see if contract is created
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print("\nNew Request for charging! Auction ID: ", request_id)
        evchargingmarket.events.LogReqCreated().processReceipt(tx_receipt)

        # sleep this program until auction is over
        time.sleep(auction_time)

        # close the Auction for the request
        tx_hash = evchargingmarket.functions.closeAuction(request_id).transact()
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print("\nClosing the auction now...")
        # time.sleep(10)