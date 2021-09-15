# import dependencies
import json
from web3 import Web3
import asyncio
# from eth_tester import EthereumTester
from random import randint
import time
import threading

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

# getting the list of all accounts on the network
accounts_list = w3.eth.get_accounts()

# separating the EV addresses 2/3rd of the network
separator = int((len(w3.eth.get_accounts()) - 1) / 3) + 1
CS_addresses = accounts_list[1 : separator]

# dictionaries to hold auction information
auc_dict = {}
seller_dict = {}
print("\nWaiting for request...")

# Function to re-do failed auction
def request_failed(buyer_address, auc_id, error_type):
    if error_type == 0:
        print(f"\n[ID: {auc_id}] No bids received for the auction...")
    elif error_type == 1:
        print(f"\n[ID: {auc_id}] Seller prices were not less than asking price!")

    tx_hash = evchargingmarket.functions.evAuctionFail(buyer_address, auc_id).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"Sending re-do request for auction...")

# seller report sending function
def send_seller_report(auc_id):
    seller_address = (evchargingmarket.functions.contracts(auc_id).call())[1]

    tx_hash = evchargingmarket.functions.setSellerMeterReport(auc_id, True).transact({'from': seller_address})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"[ID: {auc_id}] Seller meter report sent...")
    print(f"[ID: {auc_id}] Contract State: {evchargingmarket.functions.contracts(auc_id).call()[10]}")

# close reveal as buyer and send buyer report
def close_reveal(auc_id):
    buyer_address = (evchargingmarket.functions.contracts(auc_id).call())[0]

    tx_hash = evchargingmarket.functions.endReveal(auc_id).transact({'from': buyer_address})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"\n[ID: {auc_id}] Reveal Ended...")

    tx_hash = evchargingmarket.functions.setBuyerMeterReport(auc_id, True).transact({'from': buyer_address})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"[ID: {auc_id}] Buyer meter report sent...")

    send_seller_report(auc_id)


# offer revealing function
def reveal_offer(auc_id):
    print(f"\n[ID: {auc_id}] Waiting for auction to close...")
    while True:
        # when all CS's are done sending their bids check to see if the auction closed
        if evchargingmarket.functions.getAuctionState(auc_id).call():
            break
        time.sleep(2)   # Check every 2 seconds to see if auction is closed
    print(f'[ID: {auc_id}] Auction closed... Revealing offers...')
    print(f"[ID: {auc_id}] The number of bids received is: {evchargingmarket.functions.getNumBids(auc_id).call()}")

    for seller_address in auc_dict[auc_id].keys():

        bid_id = auc_dict[auc_id][seller_address][0]
        price = auc_dict[auc_id][seller_address][1]

        tx_hash = evchargingmarket.functions.revealOffer(auc_id, price, bid_id).transact({'from': seller_address})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    close_reveal(auc_id)



# event handling function
def handle_event(auc_id, _time, buyer, max_price):
    # reset the seller dictionary for given charging request
    seller_dict = {}
    price_list = []

    # get the auction ID from event
    index = 0
    buyer_price = evchargingmarket.functions.contracts(auc_id).call()[3]

    # every CS sends in a bid for now with random prices from 0 - _maxPrice
    for seller_address in CS_addresses:
        # skip loop if auction time frame has passed
        if (time.time() > _time):
            continue
        # hard cap of 20 seller bids on any auction'
        # if index >= 20:
        #     break
        
        # select a CS to submit a sealed bid and store its price
        price = randint(5, 50)
        sealed_bid = evchargingmarket.functions.getHash(price).call({'from': seller_address})
        seller_dict[seller_address] = [index, price]
        price_list.append(price)
        index += 1

        tx_hash = evchargingmarket.functions.makeSealedOffer(auc_id, sealed_bid).transact({'from': seller_address}) 
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    auc_dict[auc_id] = seller_dict

    print(f"\n[ID: {auc_id}] Sent new sealed bids!")
    print()
    print(f"[ID: {auc_id}] {price_list}")
    # Add if index == 0 error for no bids sent
    if index == 0:
        request_failed(buyer, auc_id, 0)
    elif min(price_list) < max_price:
        reveal_offer(auc_id)
    else:
        request_failed(buyer, auc_id, 1)
    print("\nWaiting for request...")


# asynchronous defined function to loop
# this func. sets up an event filter and is looking for new entries for the event "LogReqCreated"
# this loop runs on a poll interval
async def log_loop(event_filter, poll_interval):
    while True:
        for LogReqCreated in event_filter.get_new_entries():
            thread = threading.Thread(target = handle_event, args = (
                LogReqCreated['args']['_aucId'],
                LogReqCreated['args']['_time'],
                LogReqCreated['args']['buyer'],
                LogReqCreated['args']['_maxPrice']))
            thread.start()
            print(f"[Active Processes] {threading.active_count() - 1}")
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