from web3 import Web3
import json
import time
import asyncio
from random import randint
import threading

with open("address.info", "r") as file_obj:
	file_info = file_obj.readlines()

contract_address = file_info[0][:-1]	# there is a \n at the end of the address in address.info
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
EV_addresses = accounts_list[1: 5]
buyer_dict = {}

def send_sealed_req(buyer, auc_id, auc_time):
    global buyer_dict

    if time.time() < auc_time:
        print(f"\n[ID:{auc_id}][0x...{buyer[-4:]}] Sending Sealed Request...")

        # Determining Price using random number and storing it in buyer_dict
        price = randint(10, 60)
        buyer_dict[auc_id][buyer] = price

        # Getting Hash of Buyer Price
        sealed_req = evchargingmarket.functions.getHash(price).call({'from': buyer})

        tx_hash = evchargingmarket.functions.makeSealedRequest(auc_id, sealed_req).transact({'from': buyer})
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"\n[ID:{auc_id}][0x...{buyer[-4:]}] Sealed Request Successfully Sent!")
    else:
        print(f"\n[ID:{auc_id}][0x...{buyer[-4:]}] ERROR: Sealed Request UNSUCCESSFUL!")

def reveal_req(buyer, auc_id, req_id):
    global buyer_dict
    print(f"\n[ID:{auc_id}][0x...{buyer[-4:]}] Waiting for Auction to Close...")
    # Wait until auction is closed to reveal request
    while True:
        if evchargingmarket.functions.getAuctionState(auc_id).call():
            break
        time.sleep(2)   # Check every 2 seconds

    print(f"\n[ID:{auc_id}][0x...{buyer[-4:]}] Revealing Request...")

    price = buyer_dict[auc_id][buyer]
    amount = randint(10, 60)

    # function revealReq(uint _aucId, uint _price, uint _amount, uint _location, uint _reqId)
    tx_hash = evchargingmarket.functions.revealReq(auc_id, price, amount, 1, req_id).transact({'from': buyer})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"\n[ID:{auc_id}][0x...{buyer[-4:]}] Request Revealed for: \nPrice: {price}\nAmount: {amount}\nRequest ID: {req_id}")

# Asynchronous Detection of Events Starts
async def log_loop(event_filter, poll_interval):
    while True:
        # event SealedReqReceived(address buyer, uint _aucId, bytes32 _sealedReq, uint _reqId);
        for sealed_req in event_filter.get_new_entries():
            thread = threading.Thread(target = reveal_req, args = (
                sealed_req['args']['buyer'],
                sealed_req['args']['_aucId'],
                sealed_req['args']['_reqId']))
            thread.start()
        await asyncio.sleep(poll_interval)

async def log_loop2(event_filter, poll_interval):
    global buyer_dict
    while True:
        # event NewAuctionCreated(uint _aucId, uint256 _time, uint256 _auctionTime);
        for new_auction in event_filter.get_new_entries():
            buyer_dict[new_auction['args']['_aucId']] = {}
            for buyer_address in EV_addresses:
                thread = threading.Thread(target = send_sealed_req, args = (
                    buyer_address,
                    new_auction['args']['_aucId'],
                    new_auction['args']['_auctionTime']))
                thread.start()
            print(f"\n[Active Processes] {threading.active_count() - 1}\n")
        await asyncio.sleep(poll_interval)

event_filter1 = evchargingmarket.events.SealedReqReceived().createFilter(fromBlock = 'latest')
event_filter2 = evchargingmarket.events.NewAuctionCreated().createFilter(fromBlock = 'latest')
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(
        asyncio.gather(
            log_loop(event_filter1, 2), log_loop2(event_filter2, 2)))
finally:
    loop.close()