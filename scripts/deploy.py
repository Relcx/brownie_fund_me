# first deploy fundme to Rinkeby test net then learn how to deploy to local ganache chain

from brownie import FundMe, MockV3Aggregator, network, config
from scripts.helpful_script import (
    get_account,
    deploy_mocks,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)


def deploy_fund_me():
    # putting get_account() in helpful_script.py
    account = get_account()
    # deploy is making a state change so have to specify from where
    # publish and verify our contract to etherscan allows us to interact with contract once verified
    # like what we had on remix, interact like click buttons to call functions and stuff
    # publish_source is submit our code for publish and verify, that's it
    # we don't need to tell brownie that we already saved our etherscan API key(ETHERSCAN_TOKEN) in .env file
    # Always fail to verify.

    # pass the price feed address to our fundme contract (for constructor to get the pricefeed)
    # any variable we want to pass to constructor can be added to deploy() function
    # if we are on a persistent network like rinkeby, we can use the associated address: "0x8A753747A1Fa494EC906cE90E9f37563A8AF630e"
    # otherwise, deploy mock
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        price_feed_address = config["networks"][network.show_active()][
            "eth_usd_price_feed"
        ]
    # brownie built-in forking mechanisms does not come with its own account so we need to add our own custome mainnet-fork network
    # remember to go back and check the video on how to use Infura, i think i probably deleted Infura's mainnet-fork by accident
    # Use single quote on fork='' so that we can pass in parameter WEB3_...
    # Note that forking from infura will get slower performance, the teacher perfers forking from alchemy.io instead. 6:01
    # use command : brownie networks add development mainnet-fork-dev cmd=ganache-cli host=http://127.0.0.1 fork='https://mainnet.infura.io/v3/$WEB3_INFURA_PROJECT_ID' accounts=10 mnemonic=brownie port=8545
    # teacher perfers forking from alchemy's mainnet, hence fork=https://eth-mainnet.alchemyapi.io/v2/Pn0cZn3hrVmJBYTSuOP_JVpMKUAiDRk6

    else:
        deploy_mocks()
        price_feed_address = MockV3Aggregator[-1].address

    fund_me = FundMe.deploy(
        price_feed_address,
        {"from": account},
        # using get("verify") will work even if we forgot to add 'verify' section in config file
        publish_source=config["networks"][network.show_active()].get("verify"),
    )
    print(f"Contract deployed to {fund_me.address}")
    return fund_me


def main():
    deploy_fund_me()


# FundMe.sol has pricefeed address from rinkeby network, it's hardcoded and hence our code currently only works with rinkeby
# However, we want to be able to deploy this contract on our local ganache chain,
# 2 methods
# 1. Mocking (deploy a fake price feed contract on ganache), this is a common practice in industry.
# 2. Forking (fork, download, a simulated chain)
