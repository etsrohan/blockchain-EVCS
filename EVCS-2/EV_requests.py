from web3 import Web3
import json
import time
from random import randint
import asyncio
import threading

AUCTION_TIME = 10
POLL_INTERVAL = 5

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

separator = len(accounts_list) // 2
# separating the EV addresses 2/3rd of the networks
EV_addresses = accounts_list[1 : separator]

# Function to close an opened auction
def close_auction(buyer_address, auc_id, auc_time, price):
    print(f"\n[ID: {auc_id}] New request - Auction Open!")
    print(f"[ID: {auc_id}] Max bid price from buyer: {price}")
    # wait until the auction closes
    while time.time() < auc_time:
        time.sleep(2)
    # close the auction with specified auction id
    tx_hash = evchargingmarket.functions.closeAuction(auc_id).transact({'from': buyer_address})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"\n[ID: {auc_id}] Closing the auction now...")

# Function to randomly select an EV address and send a charging request
def send_ev_request(buyer_address = None, _id = None):

    # Creating charging request by a random user
    if buyer_address == None:
        buyer_address = EV_addresses[randint(0, len(EV_addresses) - 1)]
    else:
        print("\n[ERROR]: Auction Failed! Auction ID: ", _id)
        print("Resending request for address: ", buyer_address)

    amount = randint(10, 60)
    price = randint(10, 60)

    # New request ID for new auction
    tx_hash = evchargingmarket.functions.createReq(amount, price, int(time.time()) + AUCTION_TIME, AUCTION_TIME, 5).transact({'from': buyer_address})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("\nNew request from EV")


# asynchronous defined function to loop
# this func. sets up an event filter and is looking for new entries for the event "LogReqCreated" and "RequestFailed"
# this loop runs on a poll interval
async def log_loop(event_filter, poll_interval, select):
    while True:
        for event in event_filter.get_new_entries():
            if event['event'] == 'LogReqCreated':
                thread = threading.Thread(target = close_auction,
                                          args = (event['args']['buyer'],
                                                  event['args']['_aucId'],
                                                  event['args']['_time'],
                                                  event['args']['_maxPrice']))
            elif event['event'] == 'RequestFailed':
                thread = threading.Thread(target = send_ev_request,
                                          args = (event['args']['buyer'],
                                                  event['args']['_id']))
            thread.start()
        if select == 1:
            thread = threading.Thread(target = send_ev_request, args = ())
            thread.start()
            await asyncio.sleep(poll_interval)
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        else:
            await asyncio.sleep(2)

# main function
# creates a filter for the latest block and looks for "LogReqCreated" from EVChargingMarket contract
# try to run log_loop function above every 2 secs
def main():
    event_filter_1 = evchargingmarket.events.LogReqCreated().createFilter(fromBlock = 'latest')
    event_filter_2 = evchargingmarket.events.RequestFailed().createFilter(fromBlock = 'latest')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(event_filter_1, POLL_INTERVAL, 0), log_loop(event_filter_2, POLL_INTERVAL, 1)))
    finally:
        loop.close()


# main function init
main()