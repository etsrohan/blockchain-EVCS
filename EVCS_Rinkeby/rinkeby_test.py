from web3 import Web3
from web3.middleware import geth_poa_middleware

INFURA_URL  = "https://rinkeby.infura.io/v3/ec9d7ab198984284b62af4c1f4e27763"
ACCOUNTS_LIST = ["0x013E38F0670e13F252ce2C041239Ca1DdE7DC393",
				 "0x11C9c3Fc3Dab31bf29FdcbCb4D8E3CE48586896F",
				 "0xab5314EEfC7B540F25B12Ca452D10301317353B8",
				 "0x2fa6C186fCBf88be8A6fAdf5f8e55f030a74e009",
				 "0xA3cA01A05dF984A6610EaF936adb606DFb4225bc",
				 "0xF1C273173d39504CA0D248F780D53a43A9a10c7f",
				 "0xFD4271113d4635f6adf9482E2819A450eB2d831A",
				 "0xeF4b3BC22F5583266eB26eb623FB7b23d5d43ae7",
				 "0x4c3d603edCC98320d9B1D8ef52415FdDb8106cCB",
				 "0xDC37ce5496d51da209134aD9Dd39Ac8df5dc4642"]
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

print(w3.isConnected())
print(w3.eth.blockNumber)

for address in ACCOUNTS_LIST:
	balance = w3.eth.getBalance(address)
	print(w3.fromWei(balance, "ether"))

w3.middleware_onion.inject(geth_poa_middleware, layer=0)

print(w3.eth.get_accounts())
print(w3.clientVersion)