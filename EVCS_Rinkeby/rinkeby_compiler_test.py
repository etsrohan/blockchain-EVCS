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

print("Bytecode:")
print(bytecode)
print("ABI:")
print(abi)
print("[SUCCESS] Compiler working correctly...")