from web3 import Web3, middleware
from web3.exceptions import ContractLogicError
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import *
from solcx import compile_source
import json
import os

# Global Constants
INFURA_URL = "https://rinkeby.infura.io/v3/ec9d7ab198984284b62af4c1f4e27763"
ADDR = "0x013E38F0670e13F252ce2C041239Ca1DdE7DC393"
PRIVATE_KEY = "b22e9f365e9e2512b0ed58bbed53264d4866ae07684148f2456e9d832a3dbd42"

# Import and Compile solidity smart contract
with open("EnergyTradingAuction.sol", "r") as file_obj:
	compiled_sol = compile_source(file_obj.read())

# retrieve the contract interface
contract_id, contract_interface = compiled_sol.popitem()

# getting bytecode / bin
bytecode = contract_interface['bin']
# getting abi
abi = contract_interface['abi']

# web3.py instance
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# set pre-funded account as deployer
w3.eth.default_account = ADDR

if w3.isConnected():
	print("[CONNECTED] Connection to Rinkeby Ethereum Test Network Established!!!")

# Adding Geth Middleware
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
w3.middleware_onion.add(middleware.simple_cache_middleware)

strategy = construct_time_based_gas_price_strategy(15)
w3.eth.setGasPriceStrategy(strategy)

EVChargingMarket = w3.eth.contract(abi=abi, bytecode=bytecode)

nonce = Web3.toHex(w3.eth.getTransactionCount(ADDR))
gas_price = w3.eth.generateGasPrice()
print("Gas Price: ", gas_price)

tr = {
	'to': None,
	'value': Web3.toHex(0),
	'gasPrice': Web3.toHex(gas_price),
	'nonce': nonce,
	'data': "0x" + bytecode,
	'gas': 5000000,
}


# submit transaction that deploys the contract
signed = w3.eth.account.sign_transaction(tr, PRIVATE_KEY)
tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)

# wait for the transaction to be mined and get the transaction receipt
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Saving contract info...")
with open("address_rinkeby.info", "w") as file_obj:
	file_obj.write(tx_receipt.contractAddress)
	file_obj.write('\n')
	file_obj.write(json.dumps(abi))
print("[SUCCESS] Saved Smart Contract Information.")

evchargingmarket = w3.eth.contract(
	address = tx_receipt.contractAddress,
	abi = abi
)
print("[SUCCESS] Energy Trading Auction Smart Contract Successfully on Rinkeby Network")
print(f"Smart Contract Address: {tx_receipt.contractAddress}")