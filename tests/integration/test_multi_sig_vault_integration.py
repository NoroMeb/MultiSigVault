import eth_utils
from scripts.deploy import deploy, FUND_AMOUNT, set_owners
from web3 import Web3
from brownie import MultiSigVault


def test_multi_sig_vault(skip_local_testing):
    # Arrange
    skip_local_testing
    multi_sig_vault = MultiSigVault[-1]
    owners = set_owners()
    value = Web3.toWei(0.001, "ether")
    data = eth_utils.to_bytes(hexstr="0x")
    reciever_inital_balance = owners[1].balance()
    multi_sig_vault_inital_balance = multi_sig_vault.balance()
    tx_id = 3
    # Act
    multi_sig_vault.submitTransaction(owners[1], value, data, {"from": owners[0]})
    multi_sig_vault.approveTransaction(tx_id, {"from": owners[0]})
    multi_sig_vault.approveTransaction(tx_id, {"from": owners[1]})
    multi_sig_vault.executeTransaction(tx_id, {"from": owners[0]})

    # Assert
    assert owners[1].balance() > reciever_inital_balance
    assert multi_sig_vault.balance() < multi_sig_vault_inital_balance
