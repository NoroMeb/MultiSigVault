from scripts.deploy import deploy, MIN_REQUIRED, OWNERS_NUM, set_owners, FUND_AMOUNT
from scripts.utils import get_account
from brownie import MultiSigVault, exceptions
import pytest
import eth_utils


def test_deploy(skip_live_testing):
    # Arrange
    skip_live_testing
    account = get_account()
    owners = set_owners()
    owners = [str(owner) for owner in owners]
    # Act
    multi_sig_vault = MultiSigVault.deploy(owners, MIN_REQUIRED, {"from": account})

    # Assert
    assert multi_sig_vault.minRequired() == MIN_REQUIRED
    for i, owner in enumerate(owners):
        assert multi_sig_vault.isOwner(owner) == True
        assert multi_sig_vault.owners(i) == owner
    with pytest.raises(exceptions.VirtualMachineError):
        MultiSigVault.deploy([], MIN_REQUIRED, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        MultiSigVault.deploy(owners, OWNERS_NUM + 1, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        MultiSigVault.deploy(owners, 0, {"from": account})
    with pytest.raises(exceptions.VirtualMachineError):
        MultiSigVault.deploy(
            [account.address, account.address], MIN_REQUIRED, {"from": account}
        )

    return multi_sig_vault


def test_submit_transaction(skip_live_testing):
    # Arrange
    skip_live_testing
    multi_sig_vault = test_deploy(skip_live_testing)
    owners = set_owners()
    to = get_account(index=6)
    value = FUND_AMOUNT
    data = eth_utils.to_bytes(hexstr="0x")
    submiter = owners[0]
    non_owner = get_account(index=7)
    # Act
    multi_sig_vault.submitTransaction(to, value, data, {"from": submiter})

    # Assert
    assert multi_sig_vault.transactions(0)["to"] == to
    assert multi_sig_vault.transactions(0)["value"] == value
    with pytest.raises(exceptions.VirtualMachineError):
        multi_sig_vault.submitTransaction(to, value, data, {"from": non_owner})

    return multi_sig_vault


def test_approve_transaction(skip_live_testing):
    # Arrange
    skip_live_testing
    multi_sig_vault = test_submit_transaction(skip_live_testing)
    owner = set_owners()[0]
    non_owner = get_account(index=7)
    tx_id = 0

    # Act
    multi_sig_vault.approveTransaction(tx_id, {"from": owner})

    # Assert
    assert multi_sig_vault.approved(tx_id, owner) == True
    with pytest.raises(exceptions.VirtualMachineError):
        multi_sig_vault.approveTransaction(tx_id, {"from": owner})
    with pytest.raises(exceptions.VirtualMachineError):
        multi_sig_vault.approveTransaction(tx_id, {"from": non_owner})

    with pytest.raises(exceptions.VirtualMachineError):
        tx_id = 1
        multi_sig_vault.approveTransaction(tx_id, {"from": owner})

    with pytest.raises(exceptions.VirtualMachineError):
        multi_sig_vault.transactions(tx_id)["executed"] = True
        multi_sig_vault.approveTransaction(tx_id, {"from": owner})

    return multi_sig_vault


def test_execute_transaction(skip_live_testing):
    # Arrange
    skip_live_testing
    multi_sig_vault, owners = deploy()
    to = get_account(index=6)
    to_initial_balance = to.balance()
    value = FUND_AMOUNT
    data = eth_utils.to_bytes(hexstr="0x")
    submiter = owners[0]
    approver_1 = owners[1]
    approver_2 = owners[2]
    multi_sig_vault.submitTransaction(to, value, data, {"from": submiter})
    multi_sig_vault.approveTransaction(0, {"from": approver_1})
    multi_sig_vault.approveTransaction(0, {"from": approver_2})

    # Act
    multi_sig_vault.executeTransaction(0, {"from": submiter})

    # Assert
    assert to.balance() == to_initial_balance + value


def test_revoke_transaction(skip_live_testing):
    # Arrange
    skip_live_testing
    multi_sig_vault = test_approve_transaction(skip_live_testing)
    owner = set_owners()[0]

    # Act
    multi_sig_vault.revokeTransaction(0, {"from": owner})

    # Assert
    assert multi_sig_vault.approved(0, owner) == False
