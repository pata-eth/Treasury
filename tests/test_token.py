from brownie import accounts, ZERO_ADDRESS, reverts


def test_token_retrieve(treasury, token1, token2, gov, whale):
    token1.transfer(treasury, 1e10, {"from": whale})
    token2.transfer(treasury, 1e20, {"from": whale})

    before_bal_1 = token1.balanceOf(gov)
    before_bal_2 = token2.balanceOf(gov)

    treasury.sweep([token1, token2], [1e10, 1e20], {"from": gov})

    after_bal_1 = token1.balanceOf(gov)
    after_bal_2 = token2.balanceOf(gov)

    assert token1.balanceOf(treasury) == 0
    assert token2.balanceOf(treasury) == 0
    assert after_bal_1 > before_bal_1
    assert after_bal_2 > before_bal_2

    print(after_bal_1 / 1e8, before_bal_1 / 1e8)
    print(after_bal_2 / 1e18, before_bal_2 / 1e18)

    accounts[0].transfer(treasury, 1e18)
    assert treasury.balance() > 0
    treasury.sweep([ZERO_ADDRESS], [1e18], {"from": gov})
    assert treasury.balance() == 0


def test_access_control(treasury, token1, token2, dev, gov, whale):
    token1.transfer(treasury, 1e10, {"from": whale})
    token2.transfer(treasury, 1e20, {"from": whale})

    with reverts():
        treasury.setGovernance(gov, {"from": dev})

    with reverts():
        treasury.sweep([token1], [1e10], {"from": dev})

    treasury.setGovernance(dev, {"from": gov})

    assert treasury.governance() == gov
    assert treasury.acceptGovernance({"from": dev})
    assert treasury.governance() == dev
