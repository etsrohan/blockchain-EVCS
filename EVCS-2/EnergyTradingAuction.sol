pragma solidity ^0.8.0;

contract EvChargingMarket { 
    enum ContractState {NotCreated, Created, HasOffer, Established, ReadyForPayment, ReportNotOk, Closed}
    enum AuctionState {Created, Closed, RevealEnd}
    
    struct Payment {
        uint bidId;
        uint256 date;
        uint energyAmount;
        bool toPay; //or toReceive
        uint total;
    }
    
    struct SealedBid {
         address bidder;
         bytes32 bid;
    }

    struct Account { // User account
        int256 balance;
        int256 energy;
        Payment[] payments;
        bool isUser;
    }
    
    struct Auction {
        uint nbBid;
        SealedBid[] bids;
        AuctionState state;
    }

    struct Contract {
        address buyer; // EV address
        address  seller; // Winner EP address
        uint  amount;   // Amount of Electriticy in kwh
        uint  buyerMaxPrice;
        uint  currentPrice;
        bool  buyerMeterReport;
        bool  sellerMeterReport; 
        uint256  deliveryTime;
        uint256  auctionTimeOut;
        uint  deliveryLocation;
        ContractState state;       
    }

    modifier auctionNotClosed(uint _aucId) {
        require(auctions[_aucId].state  == AuctionState.Created);
        _;
    }
    
    modifier auctionClosed(uint _aucId) {
        require(auctions[_aucId].state == AuctionState.Closed);
        _;
    }
    
    modifier revealNotEnded(uint _aucId) {
        require(auctions[_aucId].state != AuctionState.RevealEnd);
        _;
    }
    
    modifier auctionExist(uint _aucId) {
        require(contracts[_aucId].state != ContractState.NotCreated);
        _;
    }

    modifier auctionTimeOut(uint _aucId) {
        require(contracts[_aucId].auctionTimeOut > block.timestamp);
        _;
    }

    modifier contractEstablished(uint _aucId) {
        require(contracts[_aucId].state == ContractState.Established);
        _;
    }

    modifier reportsOk(uint _aucId) {
        require(contracts[_aucId].sellerMeterReport);
        require(contracts[_aucId].buyerMeterReport);
        _;
    }

    modifier buyerOnly(uint _aucId) {
        require(contracts[_aucId].buyer == msg.sender);
        _;
    }

    modifier sellerOnly(uint _aucId) {
        require(contracts[_aucId].seller == msg.sender);
        _;
    }

    modifier accountExist(address _user) {
        require(accounts[_user].isUser);
        _;
    }

    uint public totalAuction;

    mapping (uint => Contract) public contracts;    // mapping from Auction ID to contract struct
    mapping (uint => Auction)  auctions;            // mapping from Auction ID to auction struct
    mapping (address => Account) public accounts;   // mapping from buyer/seller to accounts struct (buyer/seller accounts)
    address auctioner;

    event LogReqCreated(	// event for new EV request creation
    	address buyer,
    	uint _aucId,
    	uint _maxPrice,
    	uint _amount,
    	uint256 _time,
    	uint256 _auctionTime,
    	uint _location
    );
    
    event LowestBidDecreased (	// event for new winner of auction
    	address _seller,
    	uint _aucId,
    	uint _price,
    	uint _amount
    );
    event FirstOfferAccepted (	// event for first charging station sending successful bid
    	address _seller,
    	uint _aucId,
    	uint _price,
    	uint _amount
    );
    event ContractEstablished (	// not used currently
    	uint _aucId,
    	address _buyer,
    	address _seller
    );
    event ReportOk(
    	uint _aucId
    );                                                                    
    event ReportNotOk(		// buyer/seller connection for payment go ahead / not go ahead
    	uint _aucId
    );
    event SealedBidReceived(	// new bid from CS received
    	address seller,
    	uint _aucId,
    	bytes32 _sealedBid, 
    	uint _bidId
    );
    event BidNotCorrectelyRevealed(	// event to show failure of bid reveal
    	address bidder,
    	uint _price,
    	bytes32 _sealedBid
    );
    
    event DoubleAuctionStart(
    	uint _aucId
    );
    
    event RequestFailed(
    	address buyer,
    	uint256 _id
    );

    function createReq(		
    	uint _amount,
    	uint _price,
    	uint256 _time,
    	uint256 _auctionTime, 
    	uint _location
    ) 
    	public
    {
        uint aucId = totalAuction++;    // Updating the totalAuction public variable and adding current auction ID to aucID
        storeAndLogNewReq(msg.sender, aucId, _amount, _price, _time, _auctionTime, _location);  // Creating new Requirement from EV
    } 

    function makeSealedOffer(
    	uint _aucId,
    	bytes32 _sealedBid
    ) 
    	public    
    	auctionExist(_aucId)
    	auctionNotClosed(_aucId) 
    	revealNotEnded(_aucId) 
    {
        auctions[_aucId].bids.push(SealedBid(msg.sender, _sealedBid));  // Appending Sealed Bid to auction bids (.push is just like .append in Python)
        uint bidId = auctions[_aucId].nbBid;    // Taking current bid ID from number of bids in auction struct
        auctions[_aucId].nbBid = bidId + 1;  // Updating number of bids to number_bids + 1 in auction struct
        emit SealedBidReceived(msg.sender, _aucId, _sealedBid, bidId);  // Emitting an event to let people know a new sealed bid was received
              
    }

    function closeAuction(
    	uint _aucId
    )
    	public
    	auctionExist(_aucId) 
    	buyerOnly(_aucId)
    	//to do: conractNotEstablished(_aucId)
    	//auctionTimeOut(_aucId)
    {
        auctions[_aucId].state = AuctionState.Closed;   // Changing the auction state to closed (from enum at the top)
    }
    
    function endReveal(
    	uint _aucId
    ) 
    	public
    	auctionExist(_aucId)
    	buyerOnly(_aucId)
    	//to do: conractNotEstablished(_aucId)
    	//auctionTimeOut(_aucId)
    {
        auctions[_aucId].state = AuctionState.RevealEnd;    // Changing auction state to RevealEnd where all bids have been received and ready to select lowest price
        contracts[_aucId].state= ContractState.Established; // Changing contract state to Established
    }
    
    function revealOffer (
    	uint _aucId,
    	uint _price,
    	uint _bidId
    ) 
    	public 
        auctionExist(_aucId)
        auctionClosed(_aucId) 
        revealNotEnded(_aucId)
    {        
        if (auctions[_aucId].bids[_bidId].bid != keccak256(abi.encodePacked(_price))) {         // keccak256 is a hashing function similar to sha32
        // Bid was not actually revealed.
        emit BidNotCorrectelyRevealed(msg.sender, _price, keccak256(abi.encodePacked(_price))); // Emitting failure that bid not revealed
        return;
        }
        if (contracts[_aucId].state == ContractState.HasOffer) {                                // checking to see if contracts struct has an offer
            if(_price < contracts[_aucId].currentPrice) {                                       // if offered price is lower than current lowest price           
                contracts[_aucId].currentPrice = _price;
                contracts[_aucId].seller = msg.sender;                                          // changing current bid winner to sender of method
                emit LowestBidDecreased(msg.sender, _aucId, _price, 0);                         // emitting that there is a new lowest bid
            }
        } 
        else {                                                                                // first offer 
            if (_price <= contracts[_aucId].buyerMaxPrice) {                                 // making sure price bid is lower than what buyer asked for
            	contracts[_aucId].currentPrice = _price;
            	contracts[_aucId].seller = msg.sender;
            	contracts[_aucId].state = ContractState.HasOffer;                                   // since it is first bidder, this bidder set to winner
            	emit FirstOfferAccepted(msg.sender, _aucId, _price, 0);                             // emit first bid offer accepted
            }
        } 
    }

    function setBuyerMeterReport(
    	uint _aucId,
    	bool _state
    )
    	public                              // this function sets status of buyer to ready / not ready for transaction
        auctionExist(_aucId)                                                                    // if seller also ready then payment begins
        contractEstablished(_aucId)
    {
        if (!_state) {
            emit ReportNotOk(_aucId);
        }
        contracts[_aucId].buyerMeterReport = _state;                                            // setting buyer meter report to say if it is ready for charging and payment
        if (contracts[_aucId].sellerMeterReport) {
            emit ReportOk(_aucId);
            contracts[_aucId].state = ContractState.ReadyForPayment;
        }
    }

    function setSellerMeterReport(	// this fucntion sets status of seller to ready / not ready for transaction
    	uint _aucId,
    	bool _state
    )
    	public
        auctionExist(_aucId)                                                                    // if buyer also ready then payment begins
        contractEstablished(_aucId)
    {
        if (!_state) {
            emit ReportNotOk(_aucId);
        }
        contracts[_aucId].sellerMeterReport = _state;                                           // setting seller meter report to say if it is ready to receive charge and payment
        if (contracts[_aucId].buyerMeterReport) {
            emit ReportOk(_aucId);
            contracts[_aucId].state = ContractState.ReadyForPayment;
        }
    }
    
    // essentially when both buyer and seller are ready to charge the payment can start
    
    function updateBalance(
    	uint _aucId,
    	address _buyer,
    	address _seller
    )
    	public 
        reportsOk(_aucId)   
    {
        uint256 date = contracts[_aucId].deliveryTime;
        uint amount = contracts[_aucId].amount;                                                 // amount is amount of electricity in kwh
        uint amountToTakeBuyer = contracts[_aucId].buyerMaxPrice * amount;
        uint amountToPaySeller = ((contracts[_aucId].currentPrice ** 2) * 25) * amount;
        uint amountToTakeAuctioner = amountToPaySeller - amountToTakeBuyer;
        // uint amountToPay = amount * (contracts[_aucId].currentPrice + contracts[_aucId].buyerMaxPrice) / 2;                        // amountToPay is money owed = electricity in kwh * rate ((lowest price + ev_bid) / 2)
        accounts[_buyer].payments.push(Payment(_aucId, date, amount, true, amountToTakeBuyer));       // payment added to buyer ledger (true is for bool toPay)
        accounts[_buyer].balance -= int256(amountToTakeBuyer);                                        // payment amount subtracted from balance
        accounts[_buyer].energy += int256(amount);
        accounts[_seller].payments.push(Payment(_aucId, date, amount, false, amountToPaySeller));     // payment added to seller ledger (false is for bool toPay - is receiving)
        accounts[_seller].balance += int256(amountToPaySeller);                                       // payment added to seller balance
        accounts[_seller].energy -= int256(amount);
        accounts[auctioner].payments.push(Payment(_aucId, date, 0, true, amountToTakeAuctioner));
        accounts[auctioner].balance -= int256(amountToTakeAuctioner);
        contracts[_aucId].state = ContractState.Closed;                                         // closing the contract so no more bids or transactions can happen
    }

    function registerNewUser(	// registering a new User using user's address
    	address _user
    ) 
    	public
    {
        //should be added by the utility only
        //later add a modifier: utilityOnly()
        accounts[_user].isUser = true;
    }

    function getReq(	// getting the contract state from enum above
    	uint _index
    ) 
    	public
    	view
    	returns(ContractState) 
    {
        return (contracts[_index].state);
    }

    function getNumberOfReq() 
    	public
    	view 
    	returns (uint) 
    {                                      // getting total number of requests from EV's
        return totalAuction;
    }

    function storeAndLogNewReq(	// New request initialization from EV
    	address _buyer,
    	uint _id,
    	uint _amount,
    	uint _price,
    	uint256 _time,
    	uint256 _auctionTime,
    	uint _location
    )
    	private
    {
        contracts[_id].buyer = _buyer;                                                          // set buyer as EV who requested charging
        contracts[_id].amount = _amount;                                                        // set buyer amount of electricity needed in kwh
        contracts[_id].buyerMaxPrice = _price;                                                  // setting max rate for electricity as per EV request
        contracts[_id].deliveryTime = _time;                                                    // time of new request by EV
        contracts[_id].auctionTimeOut = block.timestamp + _auctionTime;                                     // time until auction closes
        contracts[_id].deliveryLocation = _location;                                            // location where the EV wants charging to be done
        contracts[_id].state = ContractState.Created;                                           
        auctions[_id].state = AuctionState.Created;                                             // Updating contract and auction states to created
        auctions[_id].nbBid = 0;                                                                // initializing the initial number of bids
        emit LogReqCreated(_buyer, _id, _price, _amount, _time, _auctionTime, _location);       // send out message to all listening that a new request was created
    }

    function addBalance(	// This function adds a certain amount of money and energy to the user's account
    	address _user,
    	int256 _amount,
        int256 _energy
    )
    	public
    {
        accounts[_user].balance += _amount;
        accounts[_user].energy += _energy;
    }

    function getHash(	// This function returns the hashed version of given price value
    	uint256 _price
    )
    	public
    	pure
    	returns(bytes32)
    {
        return keccak256(abi.encodePacked(_price));
    }

    function getAuctionState(
    	uint256 _id
    )
    	public
    	view
    	returns(AuctionState)
    {
        return auctions[_id].state;
    }

    function getNumBids(
    	uint256 _id
    )
    	public
    	view
    	returns(uint256) 
    {
        return auctions[_id].nbBid;
    }
    
    function doubleAuctionBegin(
    	uint256 _id
    )
    	public
    {
    	emit DoubleAuctionStart(_id);
    }
    
    function evAuctionFail(
    	address buyer,
    	uint256 _id
    )
    	public
    {
    	emit RequestFailed(buyer, _id);
    }

    function setAuctioner()
        public
    {
        auctioner = msg.sender;
        accounts[auctioner].balance = 1000000;
    }

}
