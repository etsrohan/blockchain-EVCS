# import dependencies
import json
import asyncio
# from eth_tester import EthereumTester
from random import randint
import time
import threading
from web3 import Web3, middleware
from web3.exceptions import ContractLogicError
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import *

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
w3.eth.setGasPriceStrategy(strategy)

print("[PROCESSING] Proceeding to CS reply program!")
# ------------------------------------------Main Program Starts Here------------------------------------------

print("\nWaiting for request...")

auctions_done = []

# # Function to re-do failed auction
# def request_failed(buyer_address, auc_id, error_type):
#     if error_type == 0:
#         print(f"\n[ID: {auc_id}] No bids received for the auction...")
#     elif error_type == 1:
#         print(f"\n[ID: {auc_id}] Seller prices were not less than asking price!")

#     tx_hash = evchargingmarket.functions.evAuctionFail(buyer_address, auc_id).transact()
#     tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

#     print(f"Sending re-do request for auction...")

# # seller report sending function
# def send_seller_report(auc_id):
#     seller_address = (evchargingmarket.functions.contracts(auc_id).call())[1]

#     tx_hash = evchargingmarket.functions.setSellerMeterReport(auc_id, True).transact({'from': seller_address})
#     tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
#     print(f"[ID: {auc_id}] Seller meter report sent...")
#     print(f"[ID: {auc_id}] Contract State: {evchargingmarket.functions.contracts(auc_id).call()[10]}")

# # close reveal as buyer and send buyer report
# def close_reveal(auc_id):
#     buyer_address = (evchargingmarket.functions.contracts(auc_id).call())[0]

#     tx_hash = evchargingmarket.functions.endReveal(auc_id).transact({'from': buyer_address})
#     tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
#     print(f"\n[ID: {auc_id}] Reveal Ended...")

#     tx_hash = evchargingmarket.functions.setBuyerMeterReport(auc_id, True).transact({'from': buyer_address})
#     tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
#     print(f"[ID: {auc_id}] Buyer meter report sent...")

#     send_seller_report(auc_id)


# # offer revealing function
# def reveal_offer(auc_id):
#     print(f"\n[ID: {auc_id}] Waiting for auction to close...")
#     while True:
#         # when all CS's are done sending their bids check to see if the auction closed
#         if evchargingmarket.functions.getAuctionState(auc_id).call():
#             break
#         time.sleep(2)   # Check every 2 seconds to see if auction is closed
#     print(f'[ID: {auc_id}] Auction closed... Revealing offers...')
#     print(f"[ID: {auc_id}] The number of bids received is: {evchargingmarket.functions.getNumBids(auc_id).call()}")

#     for seller_address in auc_dict[auc_id].keys():

#         bid_id = auc_dict[auc_id][seller_address][0]
#         price = auc_dict[auc_id][seller_address][1]

#         tx_hash = evchargingmarket.functions.revealOffer(auc_id, price, bid_id).transact({'from': seller_address})
#         tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

#     close_reveal(auc_id)

auc_dict = {}

# event handling function
def send_bid(auc_id, _time, buyer, max_price, seller):
    global auc_dict

    nonce = w3.eth.getTransactionCount(seller)
    gas_price = w3.eth.generateGasPrice()
    tr = {
       'from': seller,
        'nonce': Web3.toHex(nonce),
        'gasPrice': gas_price,
    }
    price = randint(5, 50)
    sealed_bid = evchargingmarket.functions.getHash(price).call({'from': seller})
    if time.time() < _time:
        print(f"[{seller}] Sending bid: {price}")
        txn = evchargingmarket.functions.makeSealedOffer(auc_id, sealed_bid).buildTransaction(tr)
        signed = w3.eth.account.sign_transaction(txn, ACCOUNTS_DICT[seller])
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        auc_dict[auc_id][seller] = price
        print(f"[SUCCESS][{seller}] Sent bid: {price} Successfully!")
    else:
        print(f"[ERROR][{seller}] Sent bid: {price} Unsuccessful!")


# asynchronous defined function to loop
# this func. sets up an event filter and is looking for new entries for the event "LogReqCreated"
# this loop runs on a poll interval
async def log_loop(event_filter, poll_interval):
    while True:
        for LogReqCreated in event_filter.get_new_entries():
            if LogReqCreated['args']['_aucId'] in auc_dict.keys():
                continue
            auc_dict[LogReqCreated['args']['_aucId']] = {}
            print(f"[{LogReqCreated['args']['_aucId']}] New Request Received!!!")
            for seller_address in ACCOUNTS_LIST[5:]:
                thread = threading.Thread(target = send_bid, args = (
                    LogReqCreated['args']['_aucId'],
                    LogReqCreated['args']['_time'],
                    LogReqCreated['args']['buyer'],
                    LogReqCreated['args']['_maxPrice'],
                    seller_address))
                thread.start()
            print(f"\n[Active Processes] {threading.active_count() - 1}\n")
            # print(LogReqCreated)
        await asyncio.sleep(poll_interval)


# main function
# creates a filter for the latest block and looks for "LogReqCreated" from EVChargingMarket contract
# try to run log_loop function above every 2 secs
def main():
    event_filter = evchargingmarket.events.LogReqCreated().createFilter(fromBlock = 'latest')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(event_filter, 2)))
    finally:
        loop.close()


# main function init
main()