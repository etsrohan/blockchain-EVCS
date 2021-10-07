# import dependencies
import json
from web3 import Web3
import asyncio
from eth_tester import EthereumTester
from random import randint
import time

with open("address.info", "r") as file_obj:
    file_info = file_obj.readlines()

contract_address = file_info[0][:-1]    # there is a \n at the end of the address in address.info
abi = json.loads(file_info[1])

ganache_url = 'HTTP://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(ganache_url))
w3.eth.default_account = w3.eth.accounts[0]

evchargingmarket = w3.eth.contract(
    address = contract_address,
    abi = abi
)

curr_block = 0
prev_block = 0
curr_time = time.time()
prev_time = 0

# Infinite loop of waiting for meter reports to come back and update balance of seller/buyer
print("\nWaiting for meter reports to come back as ok...")
def handle_event(event):
	global prev_block
	global curr_block
	global prev_time
	global curr_time

	auc_id = event['args']['_aucId']
	buyer_address = (evchargingmarket.functions.contracts(auc_id).call())[0]
	seller_address = (evchargingmarket.functions.contracts(auc_id).call())[1]

	tx_hash = evchargingmarket.functions.updateBalance(auc_id, buyer_address, seller_address).transact()
	tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

	# Getting number of transactions per second
	prev_block = curr_block
	curr_block = w3.eth.blockNumber
	prev_time = curr_time
	curr_time = evchargingmarket.functions.contracts(auc_id).call()[8]
	transactions_per_second = (curr_block - prev_block) / (curr_time - prev_time)

	print("\nUpdated balances of buyer and seller...")
	print("Seller balance: ", evchargingmarket.functions.accounts(seller_address).call()[0])
	print("Buyer balance: ", evchargingmarket.functions.accounts(buyer_address).call()[0])
	print("Total Transactions: ", curr_block - prev_block)
	print("Transactions Per Second: ", transactions_per_second)


async def log_loop(event_filter, poll_interval):
    while True:
        for report_ok in event_filter.get_new_entries():
            handle_event(report_ok)
        await asyncio.sleep(poll_interval)

event_filter = evchargingmarket.events.ReportOk().createFilter(fromBlock = 'latest')
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(
        asyncio.gather(
            log_loop(event_filter, 2)))
finally:
    loop.close()