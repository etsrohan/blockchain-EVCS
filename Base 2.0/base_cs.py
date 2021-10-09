# import dependencies
import json
from web3 import Web3
import asyncio
from random import randint
import time

with open("address.info", "r") as file_obj:
    file_info = file_obj.readlines()

contract_address = file_info[0][:-1]    # there is a \n at the end of the address in address.info
abi = json.loads(file_info[1])

# print(contract_address)
# print()
# print(abi)

ganache_url = 'HTTP://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(ganache_url))
w3.eth.default_account = w3.eth.accounts[0]

evchargingmarket = w3.eth.contract(
    address = contract_address,
    abi = abi
)

# getting the list of all accounts on the network
accounts_list = w3.eth.get_accounts()

# separating the EV addresses 2/3rd of the networks
separator = int((len(w3.eth.get_accounts()) - 1) / 3) + 1
CS_addresses = accounts_list[1 : separator]

# dictionaries to hold auction information
auc_dict = {}
seller_dict = {}
print("\nWaiting for request...")

# seller report sending function
def send_seller_report(auc_id):
    w3.eth.default_account = (evchargingmarket.functions.contracts(auc_id).call())[1]

    tx_hash = evchargingmarket.functions.setSellerMeterReport(auc_id, True).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("\nSeller meter report sent...")

# close reveal as buyer and send buyer report
def close_reveal(auc_id):
    w3.eth.default_account = (evchargingmarket.functions.contracts(auc_id).call())[0]

    tx_hash = evchargingmarket.functions.endReveal(auc_id).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("\nReveal Ended...")

    tx_hash = evchargingmarket.functions.setBuyerMeterReport(auc_id, True).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("\nBuyer meter report sent...")

    send_seller_report(auc_id)


# offer revealing function
def reveal_offer(auc_id):
    print("\nWaiting for auction to close...")
    while True:
        # when all CS's are done sending their bids check to see if the auction closed
        if evchargingmarket.functions.getAuctionState(auc_id).call():
            break
        time.sleep(2)   # Check every 2 seconds to see if auction is closed
    print('\nAuction closed... Revealing offers...')
    print("The number of bids received is: " + str(evchargingmarket.functions.getNumBids(auc_id).call()))

    for seller_address in auc_dict[auc_id].keys():
        w3.eth.default_account = seller_address

        bid_id = auc_dict[auc_id][seller_address][0]
        price = auc_dict[auc_id][seller_address][1]

        tx_hash = evchargingmarket.functions.revealOffer(auc_id, price, bid_id).transact()
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    close_reveal(auc_id)



# event handling function
def handle_event(event):
    # reset the seller dictionary for given charging request
    seller_dict = {}

    # get the auction ID from event
    auc_id = event['args']['_aucId']
    index = 0

    # every CS sends in a bid for now with random prices from 0 - _maxPrice
    for seller_address in CS_addresses:
        # skip loop if auction time frame has passed
        if (time.time() > event['args']['_time']):
            continue
        
        # select a CS to submit a sealed bid and store its price
        w3.eth.default_account = seller_address
        price = randint(1, event['args']['_maxPrice'])
        sealed_bid = evchargingmarket.functions.getHash(price).call()
        seller_dict[seller_address] = [index, price]
        index += 1

        tx_hash = evchargingmarket.functions.makeSealedOffer(auc_id, sealed_bid).transact()    
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    auc_dict[auc_id] = seller_dict

    print("\nSent new sealed bids!")
    print()
    print(auc_dict)
    reveal_offer(auc_id)
    print("\nWaiting for request...")


# asynchronous defined function to loop
# this func. sets up an event filter and is looking for new entries for the event "LogReqCreated"
# this loop runs on a poll interval
async def log_loop(event_filter, poll_interval):
    while True:
        for LogReqCreated in event_filter.get_new_entries():
            handle_event(LogReqCreated)
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
if __name__ == "__main__":
    main()