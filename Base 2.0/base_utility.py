# import dependencies
import json
from web3 import Web3
import asyncio
from random import randint
import time
import threading

AUCTION_TIME = 15
REVEAL_TIME = 10

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

# ------------------------------------Main Program------------------------------------
print("\n[UTILITY] STARTING PROGRAM...")
def open_auction():
	print("\n[Processing] Opening new Auction...")
	tx_hash = evchargingmarket.functions.createReq(int(time.time()), AUCTION_TIME).transact()
	tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

def close_auction(auc_id, close_time):
	print(f"\n[ID:{auc_id}] Waiting for Auction Close Time...")
	# Wait until auction closing time
	while True:
		if time.time() > close_time:
			break
		time.sleep(2)
	tx_hash = evchargingmarket.functions.closeAuction(auc_id).transact()
	tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
	print(f"\n[ID:{auc_id}] CLOSING AUCTION NOW!")

	close_reveal(auc_id)

def close_reveal(auc_id):
	print(f"\n[ID:{auc_id}] Waiting for Reveal Period to End...")
	time.sleep(REVEAL_TIME)

	tx_hash = evchargingmarket.functions.endReveal(auc_id).transact()
	tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
	print(f"\n[ID:{auc_id}] ENDING REVEAL NOW!")

	meter_reports(auc_id)

def meter_reports(auc_id):
	print(f"\n[ID:{auc_id}] Sending Buyer Meter Report...")

	tx_hash = evchargingmarket.functions.setBuyerMeterReport(auc_id, True).transact()
	tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

	print(f"\n[ID:{auc_id}] Sending Seller Meter Report...")
	tx_hash = evchargingmarket.functions.setSellerMeterReport(auc_id, True).transact()
	tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

	print(f"\n[ID:{auc_id}][SUCCESS] Meter Reports SENT!")

def payment_success(auc_id, buyer, seller, buyer_price, auction_price, energy):
	print(f"""
	\n[ID: {auc_id}][SUCCESS] Payment Success:
	\r\tAuction Price: {auction_price}\n\tBuyer Price: {buyer_price}
	\r\tEnergy Requested: {energy}\n\tPayment: {auction_price * energy}
	\nBuyer Details:
	\r\tAddress: {buyer}
	\r\tCurrent Balance: {evchargingmarket.functions.accounts(buyer).call()[0]}
	\r\tCurrent Energy: {evchargingmarket.functions.accounts(buyer).call()[1]}
	\nSeller Details:
	\r\tAddress: {seller}
	\r\tCurrent Balance: {evchargingmarket.functions.accounts(seller).call()[0]}
	\r\tCurrent Energy: {evchargingmarket.functions.accounts(seller).call()[1]}
	""")


def payment_failure(auc_id, buyer, seller, buyer_price, auction_price, energy):
	print(f"""
	\n[ID: {auc_id}][FAILURE] Payment Failure:
	\r\tAuction Price: {auction_price}\n\tBuyer Price: {buyer_price}
	\r\tEnergy Requested: {energy}\n\tPayment: N/A
	\nBuyer Details:
	\r\tAddress: {buyer}
	\r\tCurrent Balance: {evchargingmarket.functions.accounts(buyer).call()[0]}
	\r\tCurrent Energy: {evchargingmarket.functions.accounts(buyer).call()[1]}
	\nSeller Details:
	\r\tAddress: {seller}
	\r\tCurrent Balance: {evchargingmarket.functions.accounts(seller).call()[0]}
	\r\tCurrent Energy: {evchargingmarket.functions.accounts(seller).call()[1]}
	""")

async def log_loop(event_filter, poll_interval):
    while True:
        for pay_success in event_filter.get_new_entries():
        	thread = threading.Thread(target = payment_success, args = (
        		pay_success['args']['_aucId'],
        		pay_success['args']['buyer'],
        		pay_success['args']['seller'],
        		pay_success['args']['_bprice'],
        		pay_success['args']['_aprice'],
        		pay_success['args']['_energy']))
        	thread.start()
        await asyncio.sleep(poll_interval)

async def log_loop1(event_filter, poll_interval):
    while True:
        for pay_fail in event_filter.get_new_entries():
        	thread = threading.Thread(target = payment_failure, args = (
        		pay_fail['args']['_aucId'],
        		pay_fail['args']['buyer'],
        		pay_fail['args']['seller'],
        		pay_fail['args']['_bprice'],
        		pay_fail['args']['_aprice'],
        		pay_fail['args']['_energy']))
        	thread.start()
        await asyncio.sleep(poll_interval)

async def log_loop2(event_filter, poll_interval):
    while True:
        for new_auction in event_filter.get_new_entries():
        	thread = threading.Thread(target = close_auction, args = (
        		new_auction['args']['_aucId'],
        		new_auction['args']['_auctionTime']))
        	thread.start()
        	print(f"\n[Active Processes] {threading.active_count() - 1}\n")
        await asyncio.sleep(poll_interval)
        thread = threading.Thread(target = open_auction, args = ())
        thread.start()
        await asyncio.sleep(5)

event_filter = evchargingmarket.events.PaymentSuccess().createFilter(fromBlock = 'latest')
event_filter1 = evchargingmarket.events.PaymentFailure().createFilter(fromBlock = 'latest')
event_filter2 = evchargingmarket.events.NewAuctionCreated().createFilter(fromBlock = 'latest')
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(
        asyncio.gather(
            log_loop(event_filter, 2), log_loop1(event_filter1, 2), log_loop2(event_filter2, 4)))
finally:
    loop.close()