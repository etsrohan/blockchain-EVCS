from web3 import Web3
from solcx import compile_source
from eth_tester import EthereumTester
import json
import asyncio
import time

# Importing the Solidity source code
with open("base_energy_contract_2.sol", "r") as file_obj:
	# Solidity source code
	compiled_sol = compile_source(file_obj.read())

print("[SUCCESS] Smart Contract Compiled Successfully")

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


with open("address.info", "w") as file_obj:
	file_obj.write(tx_receipt.contractAddress)
	file_obj.write('\n')
	file_obj.write(json.dumps(abi))

print("[SUCCESS] Smart Contract Detailes Saved!")

# get all accounts addresses on network
accounts_list = w3.eth.get_accounts()

# register all known EVs and CSs
print("Registering all users and adding initial balance")
for user_address in accounts_list[1:]:
	evchargingmarket.functions.registerNewUser(user_address).transact()
	evchargingmarket.functions.addBalance(user_address, 1000000).transact()

print("[SUCCESS] Smart Contract Deployed!")