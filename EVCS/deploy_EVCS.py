from web3 import Web3
from solcx import compile_source
import json

with open("EnergyTradingAuction.sol", "r") as file_obj:
	# Importing the Solidity source code then compiling it
	compiled_sol = compile_source(file_obj.read())

# retrieve the contract interface
contract_id, contract_interface = compiled_sol.popitem()

# getting bytecode / bin
bytecode = contract_interface['bin']
# getting abi
abi = contract_interface['abi']

# web3.py instance
ganache_url = 'HTTP://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(ganache_url))

# set pre-funded account as deployer
w3.eth.default_account = w3.eth.accounts[0]

EVChargingMarket = w3.eth.contract(abi=abi, bytecode=bytecode)

print("Deploying Smart Contract...")
# submit transaction that deploys the contract
tx_hash = EVChargingMarket.constructor().transact()

# wait for the transaction to be mined and get the transaction receipt
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Saving Smart Contract Info...")
with open("address.info", "w") as file_obj:
	file_obj.write(tx_receipt.contractAddress)
	file_obj.write('\n')
	file_obj.write(json.dumps(abi))
print("Contract Info Saved!")

evchargingmarket = w3.eth.contract(
	address = tx_receipt.contractAddress,
	abi = abi,)

print("[SUCCESS] Contract Deployed Successfully!")