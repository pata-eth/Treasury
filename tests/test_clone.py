import pytest
from brownie import reverts, Contract
import test_token


def test_clone(treasury, token1, token2, dev, gov, whale):
    clone_tx = treasury.clone(gov, {"from":dev})
    cloned_treasury = Contract.from_abi(
            "Treasury", clone_tx.events["Cloned"]["clone"], treasury.abi
        )

    with reverts():
        cloned_treasury.clone(gov, {"from":dev})

    test_token.test_token_retrieve(cloned_treasury, token1, token2, gov, whale)
    test_token.test_access_control(cloned_treasury, token1, token2, dev, gov, whale)
