import pytest
import asyncio
import aiohttp
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


def test_exception_invalid_wallet(loop):
    response = False
    try:
        loop.run_until_complete(apirone_api.ApironeSaving("tyujytrew").balance())
    except apirone_api.exceptions.InvalidWallet:
        response = True

    assert response


@pytest.mark.parametrize("amount, label, message", [
    (1, "label", "Hello apirone!"),
    (None, None, None)
])
def test_gen_qr_code(loop, amount, label, message):
    address = "3FADVJzjsmkMVVHPv7QGhSTEJWtmamJqNJ"
    url_to_qr_code = apirone.gen_qr_code("bitcoin", address, amount=amount, label=label, message=message)
    assert "image/png" == loop.run_until_complete(_request("GET", url_to_qr_code)).content_type


async def _request(*args, **kwargs):
    async with aiohttp.ClientSession() as session:
        response = await session.request(*args, **kwargs)

    return response
