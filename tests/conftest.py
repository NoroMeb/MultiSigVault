import pytest
from brownie import network
from scripts.utils import LOCAL_BLOCKCHAIN_ENVIRONMENTS


@pytest.fixture
def skip_live_testing():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing !")


@pytest.fixture
def skip_local_testing():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for live testing !")
