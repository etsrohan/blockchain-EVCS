from web3 import Web3
from solcx import compile_source
from eth_tester import EthereumTester
import json
import asyncio
import time

# Importing the Solidity source code
file_obj = open("EnergyTradingSecondPriceAuction.sol", "r")
#print(file_obj.read()) 


# Solidity source code
compiled_sol = compile_source(file_obj.read())

# Close file
file_obj.close()

# retrieve the contract interface
contract_id, contract_interface = compiled_sol.popitem()

# getting bytecode / bin
bytecode = contract_interface['bin']
# getting abi
abi = contract_interface['abi']

# web3.py instance
ganache_url = 'HTTP://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(ganache_url))

# set pre-funded account as sender
w3.eth.default_account = w3.eth.accounts[0]

EVChargingMarket = w3.eth.contract(abi=abi, bytecode=bytecode)

# submit transaction that deploys the contract
tx_hash = EVChargingMarket.constructor().transact()

# wait for the transaction to be mined and get the transaction receipt
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

evchargingmarket = w3.eth.contract(
	address = tx_receipt.contractAddress,
	abi = abi
)

file_obj = open("address.info", "w")
file_obj.write(tx_receipt.contractAddress)
file_obj.write('\n')
file_obj.write(json.dumps(abi))
file_obj.close()

# print(tx_receipt.contractAddress)
# print()
# print(type(abi))
# print(abi)
# print()

# Testing stuff
# print(evchargingmarket.functions.getNumberOfReq().call())
# print(evchargingmarket.all_functions())
# print(w3.eth.default_account)
# print()
# print(len(w3.eth.get_accounts()))

# get all accounts addresses on network
accounts_list = w3.eth.get_accounts()

# register all known EVs and CSs
print("\nRegistering all users and adding initial balance")
for user_address in accounts_list[1:]:
	evchargingmarket.functions.registerNewUser(user_address).transact()
	evchargingmarket.functions.addBalance(user_address, 1000000).transact()


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