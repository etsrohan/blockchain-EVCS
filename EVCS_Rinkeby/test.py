from web3 import Web3, middleware
from web3.exceptions import ContractLogicError
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import *
import json
import asyncio
import time
from random import randint

## Global Variables
INFURA_URL  = "https://rinkeby.infura.io/v3/ec9d7ab198984284b62af4c1f4e27763"

CONTRACT_ADDRESS = "0x396231a9997F2B56EB6E07c516D7f5ddaA096821"

# Accounts and Private Key Pairs
ACCOUNTS_DICT = {"0x013E38F0670e13F252ce2C041239Ca1DdE7DC393": "b22e9f365e9e2512b0ed58bbed53264d4866ae07684148f2456e9d832a3dbd42",
                 "0x11C9c3Fc3Dab31bf29FdcbCb4D8E3CE48586896F": "441f592eecd252dd704455740f2d0a216b92c9a824d05e30edb319a909986e19",
                 "0xab5314EEfC7B540F25B12Ca452D10301317353B8": "6fbb06c1c031b620d23f7d3297511807efdd64e8ec0e6db9e0a82005a4f7a00e",
                 "0x2fa6C186fCBf88be8A6fAdf5f8e55f030a74e009": "ccd523d78ab18cf2254baa1d042655d60e6302dc6a84305a16efdf0f68247732",
                 "0xA3cA01A05dF984A6610EaF936adb606DFb4225bc": "7998f75140c68975546e14fc15185425abb5546ecabd62b18982082b50f7c96a",
                 "0xF1C273173d39504CA0D248F780D53a43A9a10c7f": "2e1a6876a4d50afc8effead53dc1e3deb1e54c6dc4bc66cdd3fc0434463f67cb",
                 "0xFD4271113d4635f6adf9482E2819A450eB2d831A": "13b4584305a62f7604c1019a30f3b4db0a2332b5fa6dda3500a88390da27bcde",
                 "0xeF4b3BC22F5583266eB26eb623FB7b23d5d43ae7": "a8ff2bfd534fca0091bc0f199a7e09f7dc6c6d953582001d584ad541efb57fb8",
                 "0x4c3d603edCC98320d9B1D8ef52415FdDb8106cCB": "5fd2537650d85b9f698f1f151cc759a28577413ce7bd9f39755143afdef25fe3",
                 "0xDC37ce5496d51da209134aD9Dd39Ac8df5dc4642": "72c5c1ad91595866ef9d26c413073f2d8262e327716f4ddd317f330f73dc67c2"}

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

AUCTION_TIME = 60

ABI = json.loads('[{"anonymous": false, "inputs": [{"indexed": false, "internalType": "address", "name": "bidder", "type": "address"}, {"indexed": false, "internalType": "uint256", "name": "_price", "type": "uint256"}, {"indexed": false, "internalType": "bytes32", "name": "_sealedBid", "type": "bytes32"}], "name": "BidNotCorrectelyRevealed", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "internalType": "uint256", "name": "_aucId", "type": "uint256"}, {"indexed": false, "internalType": "address", "name": "_buyer", "type": "address"}, {"indexed": false, "internalType": "address", "name": "_seller", "type": "address"}], "name": "ContractEstablished", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "internalType": "uint256", "name": "_aucId", "type": "uint256"}], "name": "DoubleAuctionStart", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "internalType": "address", "name": "_seller", "type": "address"}, {"indexed": false, "internalType": "uint256", "name": "_aucId", "type": "uint256"}, {"indexed": false, "internalType": "uint256", "name": "_price", "type": "uint256"}, {"indexed": false, "internalType": "uint256", "name": "_amount", "type": "uint256"}], "name": "FirstOfferAccepted", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "internalType": "address", "name": "buyer", "type": "address"}, {"indexed": false, "internalType": "uint256", "name": "_aucId", "type": "uint256"}, {"indexed": false, "internalType": "uint256", "name": "_maxPrice", "type": "uint256"}, {"indexed": false, "internalType": "uint256", "name": "_amount", "type": "uint256"}, {"indexed": false, "internalType": "uint256", "name": "_time", "type": "uint256"}, {"indexed": false, "internalType": "uint256", "name": "_auctionTime", "type": "uint256"}, {"indexed": false, "internalType": "uint256", "name": "_location", "type": "uint256"}], "name": "LogReqCreated", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "internalType": "address", "name": "_seller", "type": "address"}, {"indexed": false, "internalType": "uint256", "name": "_aucId", "type": "uint256"}, {"indexed": false, "internalType": "uint256", "name": "_price", "type": "uint256"}, {"indexed": false, "internalType": "uint256", "name": "_amount", "type": "uint256"}], "name": "LowestBidDecreased", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "internalType": "uint256", "name": "_aucId", "type": "uint256"}], "name": "ReportNotOk", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "internalType": "uint256", "name": "_aucId", "type": "uint256"}], "name": "ReportOk", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "internalType": "address", "name": "buyer", "type": "address"}, {"indexed": false, "internalType": "uint256", "name": "_id", "type": "uint256"}], "name": "RequestFailed", "type": "event"}, {"anonymous": false, "inputs": [{"indexed": false, "internalType": "address", "name": "seller", "type": "address"}, {"indexed": false, "internalType": "uint256", "name": "_aucId", "type": "uint256"}, {"indexed": false, "internalType": "bytes32", "name": "_sealedBid", "type": "bytes32"}, {"indexed": false, "internalType": "uint256", "name": "_bidId", "type": "uint256"}], "name": "SealedBidReceived", "type": "event"}, {"inputs": [{"internalType": "address", "name": "", "type": "address"}], "name": "accounts", "outputs": [{"internalType": "int256", "name": "balance", "type": "int256"}, {"internalType": "bool", "name": "isUser", "type": "bool"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "address", "name": "_user", "type": "address"}, {"internalType": "int256", "name": "_amount", "type": "int256"}], "name": "addBalance", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "_aucId", "type": "uint256"}], "name": "closeAuction", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "name": "contracts", "outputs": [{"internalType": "address", "name": "buyer", "type": "address"}, {"internalType": "address", "name": "seller", "type": "address"}, {"internalType": "uint256", "name": "amount", "type": "uint256"}, {"internalType": "uint256", "name": "buyerMaxPrice", "type": "uint256"}, {"internalType": "uint256", "name": "currentPrice", "type": "uint256"}, {"internalType": "bool", "name": "buyerMeterReport", "type": "bool"}, {"internalType": "bool", "name": "sellerMeterReport", "type": "bool"}, {"internalType": "uint256", "name": "deliveryTime", "type": "uint256"}, {"internalType": "uint256", "name": "auctionTimeOut", "type": "uint256"}, {"internalType": "uint256", "name": "deliveryLocation", "type": "uint256"}, {"internalType": "enum EvChargingMarket.ContractState", "name": "state", "type": "uint8"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "_amount", "type": "uint256"}, {"internalType": "uint256", "name": "_price", "type": "uint256"}, {"internalType": "uint256", "name": "_time", "type": "uint256"}, {"internalType": "uint256", "name": "_auctionTime", "type": "uint256"}, {"internalType": "uint256", "name": "_location", "type": "uint256"}], "name": "createReq", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "_id", "type": "uint256"}], "name": "doubleAuctionBegin", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "_aucId", "type": "uint256"}], "name": "endReveal", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "buyer", "type": "address"}, {"internalType": "uint256", "name": "_id", "type": "uint256"}], "name": "evAuctionFail", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "_id", "type": "uint256"}], "name": "getAuctionState", "outputs": [{"internalType": "enum EvChargingMarket.AuctionState", "name": "", "type": "uint8"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "_price", "type": "uint256"}], "name": "getHash", "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}], "stateMutability": "pure", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "_id", "type": "uint256"}], "name": "getNumBids", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "getNumberOfReq", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "_index", "type": "uint256"}], "name": "getReq", "outputs": [{"internalType": "enum EvChargingMarket.ContractState", "name": "", "type": "uint8"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "_aucId", "type": "uint256"}, {"internalType": "bytes32", "name": "_sealedBid", "type": "bytes32"}], "name": "makeSealedOffer", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "_user", "type": "address"}], "name": "registerNewUser", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "_aucId", "type": "uint256"}, {"internalType": "uint256", "name": "_price", "type": "uint256"}, {"internalType": "uint256", "name": "_bidId", "type": "uint256"}], "name": "revealOffer", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "_aucId", "type": "uint256"}, {"internalType": "bool", "name": "_state", "type": "bool"}], "name": "setBuyerMeterReport", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "_aucId", "type": "uint256"}, {"internalType": "bool", "name": "_state", "type": "bool"}], "name": "setSellerMeterReport", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [], "name": "totalAuction", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "_aucId", "type": "uint256"}, {"internalType": "address", "name": "_buyer", "type": "address"}, {"internalType": "address", "name": "_seller", "type": "address"}], "name": "updateBalance", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]')
# web3.py instance
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Message for successful connection to Rinkeby network
if w3.isConnected():
    print("[CONNECTED] Connection to Rinkeby Ethereum Test Network Established!!!")

# Adding Geth Middleware
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
w3.middleware_onion.add(middleware.simple_cache_middleware)

# set pre-funded account as deployer
w3.eth.default_account = ACCOUNTS_LIST[0]

evchargingmarket = w3.eth.contract(
    address = CONTRACT_ADDRESS,
    abi = ABI
)

strategy = construct_time_based_gas_price_strategy(15)
w3.eth.set_gas_price_strategy(strategy)

print("[PROCESSING] Proceeding to EV request program!")
# ------------------------------------------Main Program Starts Here------------------------------------------

print(evchargingmarket.functions.getNumBids(17).call())
for address in ACCOUNTS_LIST:
    print(evchargingmarket.functions.accounts(address).call())

print("The number of Auctions Processed: ", evchargingmarket.functions.getNumberOfReq().call())
print("[PROCESSING] Calculating Gas Price for Transactions...")
gas_price = w3.eth.generate_gas_price()
print("[COMPLETE] Gas Price: ", gas_price)

nonce = w3.eth.get_transaction_count(ACCOUNTS_LIST[0])
print("Nonce: ", nonce)