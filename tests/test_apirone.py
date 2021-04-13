import pytest
import asyncio
import apirone_api


wallet_id = "btc-bd3b35b378a21c190560eccabaf426a8"
transfer_key = "tYKd2ms3VADar3qV5E4QPnmvHU8ke3Pe"


apirone = apirone_api.ApironeSaving(wallet_id)


@pytest.fixture(scope='session')
def loop():
    return asyncio.get_event_loop()


def test_ticker(loop):
    response = loop.run_until_complete(apirone.ticker("btc"))
    assert "usd" in response


def test_create_address(loop):
    response = loop.run_until_complete(apirone.create_address(callback_url="https://github.com"))
    assert "address" in response and response["callback"] is not None


def test_balance(loop):
    response = loop.run_until_complete(apirone.balance())
    assert "available" in response
