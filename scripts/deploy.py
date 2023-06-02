from brownie import Treasury, accounts, network, chain
import click
import json


def main():
    network_name = network.show_active()
    click.echo(f"You are using the '{network_name}' network")
    dev = accounts.load(
        click.prompt("Account", type=click.Choice(accounts.load()))
    )
    click.echo(f"You are using: 'dev' [{dev.address}]")

    publish_source = False if "fork" in network_name else True
    publish_source = publish_source if "mainnet" in network_name else False

    treasury = dev.deploy(Treasury, dev, publish_source=publish_source)

    with open("build/deployments/map.json") as f:
        # trade handler helper library has safe transfer functions. validate
        # that the library was linked corectly
        trade_handler_helper = json.load(f)[str(chain.id)][
            "TradeHandlerHelper"
        ][
            0
        ]  # latest deployed

    assert (
        treasury.bytecode.find(trade_handler_helper[2:].lower()) > 0
    ), "library wasn't linked"
