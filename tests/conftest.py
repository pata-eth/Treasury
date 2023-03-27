import pytest
import json
from brownie import Contract
from brownie import Treasury, TradeHandlerHelper


@pytest.fixture
def token1():
    token_address = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"  # WBTC
    yield Contract(token_address)


@pytest.fixture
def token2():
    token_address = "0x6B175474E89094C44Da98b954EedeAC495271d0F"  # DAI
    yield Contract(token_address)


@pytest.fixture
def gov(accounts):
    addr = "0x2C01B4AD51a67E2d8F02208F54dF9aC4c0B778B6"
    accounts[0].transfer(addr, 2e18)
    yield accounts.at(addr, force=True)


@pytest.fixture
def dev(accounts):
    addr = "0x2757AE02F65dB7Ce8CF2b2261c58f07a0170e58e"
    accounts[0].transfer(addr, 5e18)
    yield accounts.at(addr, force=True)


@pytest.fixture
def whale(accounts, token1, token2):
    wbtc_whale = accounts.at(
        "0x9ff58f4fFB29fA2266Ab25e75e2A8b3503311656", force=True
    )
    dai_whale = accounts.at(
        "0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503", force=True
    )
    token1.transfer(
        dai_whale, token1.balanceOf(wbtc_whale), {"from": wbtc_whale}
    )
    yield dai_whale


@pytest.fixture
def treasury(gov, dev):
    # before deploying the library, we update it's abi to include external
    # functions.
    # non-view functions are not included in the abi by solc
    # https://github.com/ethereum/solidity/issues/7527
    #
    # Original abi after compile
    with open(
        "./build/contracts/TradeHandlerHelper.json", "r", encoding="utf-8"
    ) as file:
        abi = json.load(file)["abi"]

    # Manually created abi for safe transfer functions
    with open("./contracts/SafeTransfers.json", "r", encoding="utf-8") as file:
        safe_transfers_abi = json.load(file)["abi"]

    # update the abi of the compiled library before deployment
    TradeHandlerHelper._build["abi"] = abi + safe_transfers_abi
    dev.deploy(TradeHandlerHelper)

    treasury = dev.deploy(Treasury, gov)
    yield treasury
