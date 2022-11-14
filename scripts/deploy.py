from brownie import MultiSigVault, config, network, accounts
from web3 import Web3

from scripts.utils import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS

MIN_REQUIRED = 2
OWNERS_NUM = 4
FUND_AMOUNT = Web3.toWei(0.2, "ether")


def main():
    deploy()


def deploy():
    account = get_account()
    owners = set_owners()

    multi_sig_vault = MultiSigVault.deploy(
        owners, MIN_REQUIRED, {"from": account}, publish_source=True
    )

    multi_sig_vault.recieve({"from": account, "value": FUND_AMOUNT})

    return multi_sig_vault, owners


def set_owners():
    owners = []
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        for i in range(OWNERS_NUM):
            owners.append(get_account(index=i + 1).address)
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        owners.append(accounts.add(config["wallets"]["from_key"]))
        owners.append(accounts.add(config["wallets"]["from_key_2"]))

    print(owners)
    return owners
