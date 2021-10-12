# import dependencies
import json
from web3 import Web3
import asyncio
from random import randint
import time
import threading

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

# -----------------------------------------MAIN PROGRAM-----------------------------------------

# getting the list of all accounts on the network
accounts_list = w3.eth.get_accounts()

print("\nWaiting for New Auction To Begin")
# separating the EV addresses 2/3rd of the networks
CS_addresses = accounts_list[5: ]
seller_dict = {}

def send_sealed_offer(seller, auc_id, auc_time):
    global seller_dict

    if time.time() < auc_time:
        print(f"\n[ID:{auc_id}][0x...{seller[-4:]}] Sending Sealed Offer...")

        # Determining Price using random number and storing it in seller_dict
        price = randint(5, 50)
        seller_dict[auc_id][seller] = price

        # Getting Hash of seller Price
        sealed_offer = evchargingmarket.functions.getHash(price).call({'from': seller})

        tx_hash = evchargingmarket.functions.makeSealedOffer(auc_id, sealed_offer).transact({'from': seller})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"\n[ID:{auc_id}][0x...{seller[-4:]}] Sealed Offer Successfully Sent!")
    else:
        print(f"\n[ID:{auc_id}][0x...{seller[-4:]}] ERROR: Sealed Offer UNSUCCESSFUL!")

def reveal_offer(seller, auc_id, bid_id):
    global seller_dict
    print(f"\n[ID:{auc_id}][0x...{seller[-4:]}] Waiting for Auction to Close...")
    # Wait until auction is closed to reveal request
    while True:
        if evchargingmarket.functions.getAuctionState(auc_id).call():
            break
        time.sleep(2)   # Check every 2 seconds

    print(f"\n[ID:{auc_id}][0x...{seller[-4:]}] Revealing Offer...")

    price = seller_dict[auc_id][seller]

    tx_hash = evchargingmarket.functions.revealOffer(auc_id, price, bid_id).transact({'from': seller})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"\n[ID:{auc_id}][0x...{seller[-4:]}] Offer Revealed for: \nPrice: {price}\nBid ID:{bid_id}")

# Asynchronous Detection of Events Starts
async def log_loop(event_filter, poll_interval):
    while True:
        # event SealedBidReceived(address seller, uint _aucId, bytes32 _sealedBid, uint _bidId);
        for sealed_bid in event_filter.get_new_entries():
            thread = threading.Thread(target = reveal_offer, args = (
                sealed_bid['args']['seller'],
                sealed_bid['args']['_aucId'],
                sealed_bid['args']['_bidId']))
            thread.start()
        await asyncio.sleep(poll_interval)

async def log_loop2(event_filter, poll_interval):
    global seller_dict
    while True:
        # event NewAuctionCreated(uint _aucId, uint256 _time, uint256 _auctionTime);
        for new_auction in event_filter.get_new_entries():
            seller_dict[new_auction['args']['_aucId']] = {}
            for seller_address in CS_addresses:
                thread = threading.Thread(target = send_sealed_offer, args = (
                    seller_address,
                    new_auction['args']['_aucId'],
                    new_auction['args']['_auctionTime']))
                thread.start()
            print(f"\n[Active Processes] {threading.active_count() - 1}\n")
        await asyncio.sleep(poll_interval)

event_filter1 = evchargingmarket.events.SealedBidReceived().createFilter(fromBlock = 'latest')
event_filter2 = evchargingmarket.events.NewAuctionCreated().createFilter(fromBlock = 'latest')
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(
        asyncio.gather(
            log_loop(event_filter1, 2), log_loop2(event_filter2, 2)))
finally:
    loop.close()