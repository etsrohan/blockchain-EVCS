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

with open("address_rinkeby.info", "r") as fo:
    add_info = fo.readlines()
CONTRACT_ADDRESS = add_info[0][:-1]
ABI = json.loads(add_info[1])
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
                 "0xDC37ce5496d51da209134aD9Dd39Ac8df5dc4642": "72c5c1ad91595866ef9d26c413073f2d8262e327716f4ddd317f330f73dc67c2",
                 "0xbB66eF34814f0613a3B738288FE55553A69C44BA": "bee41af6acfa1c6f430646b8744e2f435f251db087971f38e5d9f2ea3a0b79c4",
                 "0x6a09436F3Cb7C3e871071033ABA967327499b9d4": "890d4a07e4f4aa790111fe8b2a5d07c84de8a708d51c48487416b892b905c010",
                 "0x138B9eBeC6DcF3a5293FD6F5846cCBFE7A9e856a": "a2a0d0097c87754d45cff13ecb81f697b30106db553250eea411da48ca5bef4a",
                 "0xA6e799871576a4337bB1EBf8E0CFe348209A9a1B": "ef741d30314c0cfa147f2c0f409349c587a5a27b4003b8e5cdf0490e6eaa588d",
                 "0x93e92A2Bc0c66A2887eCF5C918fbbd622491eD23": "64778725d0104b96b58dad5d21bce443b806bf322b4d58d82afc60b279532a0c",
                 "0xa72e420605FD940b860c493263ce891d434782CB": "a18a2c18ed46edb5b6c4fe2a52a69373c7929b34489ac9b193cc313ff2a01c7d",
                 "0x2CB3437FcCF9fdd7a77438d232192E2bc2F2a76D": "91b403bd0ced9eff20eb3c8bf388bdc5641fa33978770ac8487ca7406950cb0d",
                 "0xe1ac1b434331F1c57b909947eC20393819Ad462f": "d1b539ffd7dd1624370b09025ec2f6d649e9c8e7c55077370d696e181effe83a",
                 "0xD9c258d8aA168add0E5183C9725c1C7C0712868A": "b4d3426cd39722b35050289379616ff6d0dd4e8c6256881a4601daf826d2bab8",
                 "0xE9003b2Ee7Ee7E33233c05272792a0fE4e5EeE90": "b637439846fab4659ee39e98ab8655f5e2f5ca719c25fb9004426fe9d0a361dd"}

ACCOUNTS_LIST = ["0x013E38F0670e13F252ce2C041239Ca1DdE7DC393",
                 "0x11C9c3Fc3Dab31bf29FdcbCb4D8E3CE48586896F",
                 "0xab5314EEfC7B540F25B12Ca452D10301317353B8",
                 "0x2fa6C186fCBf88be8A6fAdf5f8e55f030a74e009",
                 "0xA3cA01A05dF984A6610EaF936adb606DFb4225bc",
                 "0xF1C273173d39504CA0D248F780D53a43A9a10c7f",
                 "0xFD4271113d4635f6adf9482E2819A450eB2d831A",
                 "0xeF4b3BC22F5583266eB26eb623FB7b23d5d43ae7",
                 "0x4c3d603edCC98320d9B1D8ef52415FdDb8106cCB",
                 "0xDC37ce5496d51da209134aD9Dd39Ac8df5dc4642",
                 "0xbB66eF34814f0613a3B738288FE55553A69C44BA",
                 "0x6a09436F3Cb7C3e871071033ABA967327499b9d4",
                 "0x138B9eBeC6DcF3a5293FD6F5846cCBFE7A9e856a",
                 "0xA6e799871576a4337bB1EBf8E0CFe348209A9a1B",
                 "0x93e92A2Bc0c66A2887eCF5C918fbbd622491eD23",
                 "0xa72e420605FD940b860c493263ce891d434782CB",
                 "0x2CB3437FcCF9fdd7a77438d232192E2bc2F2a76D",
                 "0xe1ac1b434331F1c57b909947eC20393819Ad462f",
                 "0xD9c258d8aA168add0E5183C9725c1C7C0712868A",
                 "0xE9003b2Ee7Ee7E33233c05272792a0fE4e5EeE90"]

AUCTION_TIME = 60

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

print("[PROCESSING] Proceeding to CS reply program!")
# ------------------------------------------Main Program Starts Here------------------------------------------

print("[PROCESSING] Calculating Gas Price for Transactions...")
gas_price = w3.eth.generate_gas_price()
print("[COMPLETE] Gas Price: ", gas_price)
print("\nWaiting for request...")
# A Dictionary containing all the bids sent by CS's for a particular Auction
# {Auction_ID -> Seller Address -> Seller Bid}
auc_dict = {}
# The Number of Bids Revealed for a particular Auction ID
count_reveal = 0
# Global variable to keep count of which group of CSs to use
cs_grp = 1

# Function that checks for reveal to end then reveals their offer
def reveal_offer(auc_id, seller, bid_id):
    global count_reveal
    print(f"\n[ID: {auc_id}][0x...{seller[-4:]}] Waiting for auction to close...")
    while True:
        # when all CS's are done sending their bids check to see if the auction closed
        if evchargingmarket.functions.getAuctionState(auc_id).call():
            break
        time.sleep(2)   # Check every 2 seconds to see if auction is closed

    nonce = w3.eth.get_transaction_count(seller)
    tr = {
        'from': seller,
        'nonce': Web3.toHex(nonce),
        'gasPrice': gas_price,
    }
    print(f"\n[ID: {auc_id}][0x...{seller[-4:]}] Revealing offer with price: {auc_dict[auc_id][seller]}, Bid ID: {bid_id}")
    txn = evchargingmarket.functions.revealOffer(auc_id, auc_dict[auc_id][seller], bid_id).buildTransaction(tr)
    signed = w3.eth.account.sign_transaction(txn, ACCOUNTS_DICT[seller])
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"\n[ID: {auc_id}][0x...{seller[-4:]}] Offer Revealed Successfully")

    # Print Contract As soon as 5 Sealers reveal their bids
    count_reveal += 1
    if count_reveal == evchargingmarket.functions.getNumBids(auc_id).call():
        print(f"\n[ID: {auc_id}] All Offers Revealed Proceeding to Meter Reports...")
        count_reveal = 0


# Function to send an individual bid
def send_bid(auc_id, _time, buyer, max_price, seller):
    global auc_dict

    nonce = w3.eth.get_transaction_count(seller)
    tr = {
        'from': seller,
        'nonce': Web3.toHex(nonce),
        'gasPrice': gas_price,
    }
    price = randint(5, 50)
    sealed_bid = evchargingmarket.functions.getHash(price).call({'from': seller})
    if time.time() < _time:
        print(f"\n[ID: {auc_id}][0x...{seller[-4:]}] Sending bid: {price}")
        txn = evchargingmarket.functions.makeSealedOffer(auc_id, sealed_bid).buildTransaction(tr)
        signed = w3.eth.account.sign_transaction(txn, ACCOUNTS_DICT[seller])
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        auc_dict[auc_id][seller] = price
        print(f"\n[ID: {auc_id}][0x...{seller[-4:]}][SUCCESS] Sent bid: {price} Successfully!")
    else:
        print(f"\n[ID: {auc_id}][0x...{seller[-4:]}][ERROR] Sent bid: {price} Unsuccessful!")


# asynchronous defined function to loop
# this func. sets up an event filter and is looking for new entries for the event "LogReqCreated"
# this loop runs on a poll interval
async def log_loop1(event_filter, poll_interval):
    global auc_dict
    global cs_grp
    while True:
        for LogReqCreated in event_filter.get_new_entries():
            if LogReqCreated['args']['_aucId'] in auc_dict:
                continue
            auc_dict[LogReqCreated['args']['_aucId']] = {}
            print(f"\n[ID: {LogReqCreated['args']['_aucId']}] New Request Received!!!")
            
            # Select correct group depending on cs_grp variable
            if cs_grp == 1:
                for seller_address in ACCOUNTS_LIST[5:10]:
                    thread = threading.Thread(target = send_bid, args = (
                        LogReqCreated['args']['_aucId'],
                        LogReqCreated['args']['_time'],
                        LogReqCreated['args']['buyer'],
                        LogReqCreated['args']['_maxPrice'],
                        seller_address))
                    thread.start()
                cs_grp = 2
            elif cs_grp == 2:
                for seller_address in ACCOUNTS_LIST[10:15]:
                    thread = threading.Thread(target = send_bid, args = (
                        LogReqCreated['args']['_aucId'],
                        LogReqCreated['args']['_time'],
                        LogReqCreated['args']['buyer'],
                        LogReqCreated['args']['_maxPrice'],
                        seller_address))
                    thread.start()
                cs_grp = 3
            else:
                for seller_address in ACCOUNTS_LIST[15:]:
                    thread = threading.Thread(target = send_bid, args = (
                        LogReqCreated['args']['_aucId'],
                        LogReqCreated['args']['_time'],
                        LogReqCreated['args']['buyer'],
                        LogReqCreated['args']['_maxPrice'],
                        seller_address))
                    thread.start()
                cs_grp = 1
            print(f"\n[Active Processes] {threading.active_count() - 1}\n")
            # print(auc_dict)
        await asyncio.sleep(poll_interval)

async def log_loop2(event_filter, poll_interval):
    bid_list = set()
    while True:
        for SealedBidReceived in event_filter.get_new_entries():
            if SealedBidReceived in bid_list:
                continue
            else:
                bid_list.add(SealedBidReceived)
            thread = threading.Thread(target = reveal_offer, args = (
                SealedBidReceived['args']['_aucId'],
                SealedBidReceived['args']['seller'],
                SealedBidReceived['args']['_bidId']))
            thread.start()
        await asyncio.sleep(poll_interval)


# main function
# creates a filter for the latest block and looks for "LogReqCreated" and "SealedBidReceived" from EVChargingMarket contract
# try to run log_loop function above every 2 secs
def main():
    event_filter1 = evchargingmarket.events.LogReqCreated().createFilter(fromBlock = 'latest')
    event_filter2 = evchargingmarket.events.SealedBidReceived().createFilter(fromBlock = 'latest')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop1(event_filter1, 2), log_loop2(event_filter2, 2)))
    finally:
        loop.close()


# main function init
main()