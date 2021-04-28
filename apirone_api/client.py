import urllib
import aiohttp

from . import exceptions


class BaseApirone:
    URL = "https://apirone.com/api"

    @staticmethod
    async def make_request(url, method="POST", **kwargs):
        async with aiohttp.ClientSession() as session:
            response = await session.request(method, url, **kwargs)

            response = await response.json()

        return response

    @staticmethod
    def convert_satoshis_to_bitcoins(sum_in_satoshis, number_of_digits=8):
        need_zero = number_of_digits - len(str(sum_in_satoshis))  # Сколько нулей ещё нужно
        _sum = "0.{}{}".format("0" * need_zero, sum_in_satoshis)
        _sum = round(float(_sum), number_of_digits)
        return _sum


class ApironeV1(BaseApirone):
    URL = "{}/v1".format(BaseApirone.URL)

    async def ticker(self, currency):
        return await self._request_v1("ticker", method="GET", params={"currency": currency})

    async def _request_v1(self, path, params=None, method="POST"):
        url = "{}/{}".format(self.URL, path)
        return await self.make_request(url, method=method, params=params)

    @staticmethod
    def gen_qr_code(currency, address, amount=None, label=None, message=None, size="200x200"):
        line = "{}:{}".format(currency, address)
        params = {}
        if amount is not None:
            params["amount"] = amount
        if label is not None:
            params["label"] = label
        if message is not None:
            params["message"] = message
        if 0 < len(params):
            params_in_str = "?{}".format(urllib.parse.urlencode(params))
        else:
            params_in_str = ""

        line = "{}{}".format(line, params_in_str)
        url = "https://chart.googleapis.com/chart?chs={}&cht=qr&chl={}".format(size, line)
        return url


class ApironeSaving(ApironeV1, BaseApirone):
    URL = "{}/v2".format(BaseApirone.URL)

    def __init__(self, wallet_id, transfer_key=None):
        self.wallet_id = wallet_id
        self.transfer_key = transfer_key

    # noinspection SpellCheckingInspection
    async def create_address(self, addr_type="p2sh-p2wpkh", callback_url=None, **callback_data):
        json_data = {"addr-type": addr_type}

        if callback_url is not None:
            json_data["callback"] = {"url": callback_url, "data": callback_data, }

        return await self._request("addresses", json=json_data)

    async def balance(self):
        response = await self._request("balance", method="GET")
        response["total"] = self.convert_satoshis_to_bitcoins(response["total"])
        response["available"] = self.convert_satoshis_to_bitcoins(response["available"])

        return response

    async def transfer(self, destinations, subtract_fee_from_amount=False, fee="normal", fee_rate=None):
        """
        https://apirone.com/ru/docs/transfer
        """
        json_data = {
            "transfer_key": self.transfer_key,
            "destinations": destinations,
            "subtract-fee-from-amount": subtract_fee_from_amount,
            "fee": fee,
        }
        if "custom" == fee:
            json_data["fee-rate"] = fee_rate

        return await self._request("transfer", json=json_data)

    async def _request(self, path, method="POST", **kwargs):
        url = "{}/{}/{}/{}".format(self.URL, "wallets", self.wallet_id, path)
        response = await self.make_request(url, method=method, **kwargs)
        return self.check_result(response)

    @staticmethod
    def check_result(json_data):
        if "message" in json_data:
            message = json_data["message"]

            if "Invalid wallet." == message:
                raise exceptions.InvalidWallet(message)

        return json_data
