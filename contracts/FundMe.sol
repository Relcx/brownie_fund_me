// SPDX-License-Identifier: MIT
pragma solidity >=0.6.6 <0.9.0;

// following is from chianlink npm package
// brownie doesn't use npm to download this package, so we need to let brownie know where (actually github) to get this package
// do it through brownie-config.yaml file, using 'dependencies:'
// also need to remap @chainlink to what's in config file to let brownie know that @chainlink is to go to github

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";

// In order to verify the solidity code (make sure it works), another thing we can do is to publish it on etherscan
// when doing it mannually, click 'verify and publish' button under contract detail on etherscan
// however, we need to paste our entire FundMe.sol code including the external packages like chainlink stuff.
// etherscan does not know how to get chainlink code, hence we will need to go to that AggregatorV3Interface.sol and
//copy paste all that code to ehterscan, this concept of copy paste whole codes is called 'flattening'.
// Brownie actually can do this programtically, need to register on etherScan and get a API key

// the interface just has function declared without any code
// Interface compile down to an ABI
// ABI = Application Binary Interface
// ABI tells solidity or other programming language
// how it can interact with another contract
// ie. what function can it call another contract with
// Note:
// Anytime you want to interact with an already deployed smart contract,
// you will need an ABI

// Note: if using solidity < 0.8, watch out for overflow
// unit8 max is 255, 255+1 = 0
// need to import safemath library from either openzepplin or chianlink
// import "@chainlink/contracts/src/v0.6/vendor/SafeMathChainlink.sol";

contract FundMe {
    // To use safemath:
    // using SafeMathChainlink for uint256; // Using is the keyword when trying to import library

    mapping(address => uint256) public addressToAmountFunded;
    address public owner;

    // For updating funder's balance after they funded the contract
    address[] public funders;

    AggregatorV3Interface public priceFeed;

    constructor(address _priceFeed) public {
        priceFeed = AggregatorV3Interface(_priceFeed);
        owner = msg.sender; // is whoever deploys this smart contract
    }

    // accept payment, payable means specifically for Ethurem
    function fund() public payable {
        // Setting minimum to be 50 USD worth of eth
        uint256 minimumUSD = 50 * 10**18; //in Wei
        // use require() is best practice instead of just use revert()
        // if requirement met, otherwise print error message.
        require(
            getConversionRate(msg.value) >= minimumUSD,
            "This is a test: you need at least 50 USD."
        );

        // Wei is the smallest denomination of ether

        // This tracks the address where some amount of ether is sent
        addressToAmountFunded[msg.sender] += msg.value;

        // get ETH -> USD conversion rate
        // use code from chainlink website
        // Note:
        // 1.decimal doesn't work in solidity
        // 2.have to use with test network, not local JavaScript VM
        //   because there is no Chainlink node on test JVM

        funders.push(msg.sender);
    }

    function getVersion() public view returns (uint256) {
        // Need to pass in the address for already deployed contract on the rinkeby chain
        // where we can get the price feed. This deployed chainlink contract holds the ETH/USD price on Rinkeby test net.
        // check ethereum price feed on chainlink documentation

        // No longer need the following line because priceFeed is already defined in constuctor and will be constucted once we deployed the contract.`
        // AggregatorV3Interface priceFeed = AggregatorV3Interface(
        //     0x8A753747A1Fa494EC906cE90E9f37563A8AF630e
        // );
        return priceFeed.version();
    }

    // Get price:
    // this calls latestRoundData() from chainlink source code which returns a tuple
    // means return(a set of different data)
    // Tuple: a list of potentially different types whose number is a constant at compile time
    // need only get the 'answer' variable from that function
    function getPrice() public view returns (uint256) {
        // priceFeed is already constucted in constuctor so no longer need to be defined here
        // AggregatorV3Interface priceFeed = AggregatorV3Interface(
        //     0x8A753747A1Fa494EC906cE90E9f37563A8AF630e
        // );

        // Get one variable from tuple:
        // 1: just redefine all the variable from origianl source code
        (
            uint80 roundId,
            int256 answer,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();
        // answer is int256 != uint256 so need to cast
        return uint256(answer * 10000000000); // in Gwei unit
        //330636067812 is actually 3306.3607 usd, decimal doesn't work in solidity

        // another way to get 'answer and get rid of the Unused variable name' warning
        // is to do:
        // (,int256 answer,,,) priceFeed.latestRoundData();
        // return uint256(answer);
    }

    // 1 eth = 1e10 Gwei = 1e18 Wei means 1 followed by 18 zeros.
    // input unit is Wei 100000000, means it is 1 Gwei
    function getConversionRate(uint256 ethAmount)
        public
        view
        returns (uint256)
    {
        uint256 ethPrice = getPrice();
        uint256 ethAmountInUsd = (ethPrice * ethAmount) / 1000000000000000000;
        // actually ethPriceUSDinGwei*ethAmount*(1/ethPriceInWei)
        return ethAmountInUsd; //329530000000 Wei is actually 0.00000032953 USD
        // since the input is 1 Gwei
    }

    // copied directly from source
    function getEntranceFee() public view returns (uint256) {
        // minimum USD
        uint256 minimumUSD = 50 * 10**18;
        uint256 price = getPrice();
        uint256 precision = 1 * 10**18;
        return (minimumUSD * precision) / price;
    }

    modifier onlyOwner() {
        require(msg.sender == owner);
        _; // means the rest of the code in the function where onlyOwner is mentioned
        // for example, when withdraw() is called, the require() part will run first
        // to verify that if it is the owner is calling this withdraw() function
        // if so, then run the rest of withdraw() function's code.
    }

    // Withdraw money
    // Modifier:
    // modifier is used to change the behavior of a function in a declarative way
    function withdraw() public payable onlyOwner {
        // sender send the fund to address of the contract,
        // contract holds the fund, then
        // require owner of the contract to be able to withdraw the whole amount
        // Need to make sure only the actual owner can be identified to be the woner
        // we could make a function 'createOwner()' but what if someone called it before the actual owner?
        // so use 'constructor', which is a function which gets executed immediately after the contract is deployed
        // require(msg.sender == owner);
        // could also use modifier when declaring the fucntion so that if we have many contracts
        // we can still make sure only owner of contract can call this fucntion

        // 'this' keyword means the contract that this line of code is currently in
        // Note: is that since Solidity 0.8, address is not payable by default.
        // And if you want to send it native currency, you need to cast it to payable first.
        payable(msg.sender).transfer(address(this).balance);

        // updating balance to 0 for all the funders by using for loop, ignoring the possibility
        // of one single address have funded multiple times.
        for (
            uint256 funderIndex = 0;
            funderIndex < funders.length;
            funderIndex++
        ) {
            address funder = funders[funderIndex];
            addressToAmountFunded[funder] = 0;
        }
        // once all balance is cleared, reset funders array to empty array
        funders = new address[](0);
        // the (0) part, I have no idea, but if I don't add this, following error:
        // Type function uint256 pure returns address[] memory is not implicitly convertible to
        // expected type address[] storage ref
    }
}
