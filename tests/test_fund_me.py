# Test should be working independtly of which network we use
# By default, when not including '--network' flag in terminal, brownie will use the default network which is by default development
# If we want to set the default network by ourselves, we could add 'default' section in config.yamal file

# In otherwords, currently, running 'brownie test' = 'brownie test --network development' which is ganache-cli

# The reason sometimes tests only run locally is because it is quicker than running tests on live networks like rinkeby

from scripts.helpful_script import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from scripts.deploy import deploy_fund_me
from brownie import network, accounts, exceptions
import pytest


def test_can_fund_and_withdraw():
    # Arrange
    account = get_account()
    # Act
    fund_me = deploy_fund_me()
    entrance_fee = fund_me.getEntranceFee() + 100
    tx = fund_me.fund({"from": account, "value": entrance_fee})
    tx.wait(1)
    # Assert
    assert fund_me.addressToAmountFunded(account.address) == entrance_fee
    tx2 = fund_me.withdraw({"from": account})
    tx2.wait(1)
    assert fund_me.addressToAmountFunded(account.address) == 0


# when trying to test only 1 function, use 'brownie test -k functionName --network rinkeby' for example,
# the test should skip this test since test_only_owner_can_withdraw() is intended for local testing
def test_only_owner_can_withdraw():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        # pytest gives up the ability to skip functions
        # note that the message "Only for local testing" did not get printed
        pytest.skip("Only for local testing")
    fund_me = deploy_fund_me()
    # create a random account and try to withdraw to test if only the owner of account can withdraw
    bad_actor = accounts.add()
    # This is telling program that if transction got reverted, then it's good
    # or in other words, telling the test_fund_me.py to expect this particular virtul machine error.
    # currently not working because always ouput: AttributeError: 'NoneType' object has no attribute '_with_attr'
    # Hence the only way to make this program run is to change exceptions.VirtualMachineError to AttributeError
    # However, feels that attribute error is before trying to interact with FundMe.sol and we need the transaction to happen
    # in order to see that only the owner of the contract can do the transaction, other random accounts trying to do the txn should be reverted
    with pytest.raises(exceptions.VirtualMachineError):
        # with pytest.raises(AttributeError):
        fund_me.withdraw({"from": bad_actor})


# git init -b main does not work in ubuntu
# use the following instead:
# git init
# git checkout -b main
# then
# git config user.name "Relcx"
# git config user.email "relcx@icloud.com"
# Note: DO NOT push your .env file to github as it contains private key information
# Add .env to .gitignore file
# git add . (will prepare all files that you want to push to git repo excluding the files specified in .gitignore, this is called staging)
# git status will show all the files that's staged to be pushed to github

# git add . will always add the new files to that staging list
# if accidently added .env by git add . then
# git rm --cached .env
# Don't forget to do git add . again to actually change that status list
