# where all the helper functions are defined
from brownie import network, config, accounts, MockV3Aggregator
from web3 import Web3

# static variables
# in order to be consistent with price unit we defined in FundMe, here we use 8 decimals instead of 18
DECIMALS = 8
# same here, since we are going to multiply price with 1e10, therefore in order to make the final price with unit of Wei,
# instead of 2000, we will need 2000,00000000
STARTING_PRICE = 200000000000

# After adding ganache-local chain to brownie
# by termial command 'brownie networks add 'brownie networks add Ethereum ganache-local host=http://127.0.0.1:8545 chainid=1337'
# Then there should be a folder called '1337' under deployments folder under build folder which will record all the deployment details for local ganache chain as well
# Remember previously that only contracts deployed to real block chain networks (like rinkeby chain with id 4) are recorded
# NOTE:
# once we closed the ganache ui, then all the contracts deployed will be lost and we have to delete 1337 folder and content associated with 1337 in map.json
# in order to run the deployment script again next time we open ganache local ui
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]


def get_account():
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


def deploy_mocks():
    print(f"The active network is: {network.show_active()}")
    print("Deploying Mocks...")
    # as per MockV3Aggregator.sol's constructor requirements, we need to specify:
    # how many decimal digits, initial price(with that many digits)
    # only deploy 1 MockV3Aggregator contract, so check if we already deployed one earlier
    if len(MockV3Aggregator) <= 0:
        MockV3Aggregator.deploy(
            # Again, in order to be consisten with price unit defined in FundMe.sol, we will just use the exact value instead of Web3.toWei()
            # DECIMALS, Web3.toWei(STARTING_PRICE, "ether"), {"from": get_account()}
            DECIMALS,
            STARTING_PRICE,
            {"from": get_account()},
        )
    # [-1] means we will use MockV3 contract that is deployed most recently
    print("Mocks Deployed!")
