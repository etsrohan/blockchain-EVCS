from web3 import Web3
import json
import time
from random import randint
import asyncio
import threading

AUCTION_TIME = 10
POLL_INTERVAL = 6

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

# separating the EV addresses 2/3rd of the networks
separator = int((len(w3.eth.get_accounts()) - 1) / 3) + 1
EV_addresses = accounts_list[separator : ]

# global variable for auction id
request_id = evchargingmarket.functions.getNumberOfReq().call()

# Function to randomly select an EV address and send a charging request
def send_ev_request(buyer_address = None, _id = None):

    global request_id
    # Creating charging request by a random user
    if buyer_address == None:
        buyer_address = EV_addresses[randint(0, len(EV_addresses) - 1)]
    else:
        print("\n[ERROR]: Auction Failed! Auction ID: ", _id)
        print("Resending request for address: ", buyer_address)

    amount = randint(10, 60)
    price = randint(10, 60)

    # New request ID for new auction
    auc_id = request_id
    request_id += 1
    tx_hash = evchargingmarket.functions.createReq(amount, price, int(time.time()) + AUCTION_TIME, AUCTION_TIME, 5).transact({'from': buyer_address})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"\n[ID: {auc_id}] New Request for charging!")
    print(f"[ID: {auc_id}] Max bid price from buyer: {price}")

    # sleep this program until auction is over
    time.sleep(AUCTION_TIME)

    # close the Auction for the request
    tx_hash = evchargingmarket.functions.closeAuction(auc_id).transact({'from': buyer_address})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"\n[ID: {auc_id}] Closing the auction now...")
    # time.sleep(10)

# event handling function
def handle_event(buyer_address, auc_id):
    send_ev_request(buyer_address = buyer_address, _id = auc_id)


# asynchronous defined function to loop
# this func. sets up an event filter and is looking for new entries for the event "LogReqCreated"
# this loop runs on a poll interval
async def log_loop(event_filter, poll_interval):
    while True:
        for RequestFailed in event_filter.get_new_entries():
            thread = threading.Thread(target = handle_event,
                                      args = (RequestFailed['args']['buyer'],
                                              RequestFailed['args']['_id']))
            thread.start()
            await asyncio.sleep(poll_interval)
        thread = threading.Thread(target = send_ev_request, args = ())
        thread.start()
        await asyncio.sleep(poll_interval)

# main function
# creates a filter for the latest block and looks for "LogReqCreated" from EVChargingMarket contract
# try to run log_loop function above every 2 secs
def main():
    event_filter = evchargingmarket.events.RequestFailed().createFilter(fromBlock = 'latest')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(event_filter, POLL_INTERVAL)))
    finally:
        loop.close()

# main function init
main()