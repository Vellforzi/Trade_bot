import json
import requests
import urllib
import hmac, hashlib
import base64
import datetime
from urllib.parse import urlparse


class Okex:
    # name and description of request method; see API stock for parameters
    methods = {
        'account': {'url': '/api/v5/account/balance', 'method': 'GET', 'private': True},
        'create_order': {'url': '/api/v5/trade/order', 'method': 'POST', 'private': True},
        'order_info': {'url': '/api/v5/trade/order', 'method': 'GET', 'private': True},
        'cancel_order': {'url': '/api/v5/trade/cancel-order', 'method': 'POST', 'private': True},
        'orders_info': {'url': '/api/v5/trade/orders-pending', 'method': 'GET', 'private': True},
        'get_positions': {'url': '/api/v5/account/positions', 'method': 'GET', 'private': True},
        'candlesticks': {'url': '/api/v5/market/candles', 'method': 'GET', 'private': False},
        'tickers': {'url': '/api/v5/market/tickers', 'method': 'GET', 'private': False}
    }

    def __init__(self, api_key, api_secret, pass_phrase, demo):
        self.api_key = api_key
        self.api_secret = bytearray(api_secret, 'utf-8')
        self.demo = demo
        self.pass_phrase = pass_phrase

        self.headers = None
        self.ts = None
        self.api_url = None
        self.method = None
        self.payload = None
        self.hash_str = None

    def _update_headers(self):
        """
        Upd headers POST or GET request to stock
        :return:
        """
        if self.methods[self.method]['private']:
            self.headers = {
                "Content-Type": "application/json",
                "OK-ACCESS-KEY": self.api_key,
                "OK-ACCESS-PASSPHRASE": self.pass_phrase,
            }
        else:
            self.headers = {
                "Content-Type": "application/json"
            }
        if self.demo:
            self.headers.update({"x-simulated-trading": '1'})  # for demo-trading this is needed

    def _ts_update(self):
        """
        Datetime for OKX format
        :return:
        """
        self.ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        self.headers.update({"OK-ACCESS-TIMESTAMP": self.ts})

    def _url_update(self):
        """
        Build the address
        :return:
        """
        self.api_url = 'https://www.okx.com' + self.methods[self.method]['url']

    def _payload_update(self):
        """
        Payload info for request; from a string for sign
        :return:
        """
        request_method = self.methods[self.method]['method']
        request_url = self.methods[self.method]['url']
        if request_method == "GET":
            payload_str = f'?{urllib.parse.urlencode(self.payload)}' if self.payload else ""
            self.api_url += payload_str
            self.req_data = ''
        else:
            payload_str = ''.join(json.dumps(self.payload).split())
            self.req_data = payload_str
        self.hash_str = f'{self.ts}{request_method}{request_url}{payload_str}'

    def _sign(self):
        """
        To sign the request by secret key
        :return:
        """
        sign = base64.b64encode(hmac.new(
            key=self.api_secret,
            msg=self.hash_str.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest())
        self.headers.update({"OK-ACCESS-SIGN": sign})

    def _prepare(self):
        if self.methods[self.method]['private']:
            self._update_headers()  # Headers upd
            self._ts_update()       # Datetime for OKX format
            self._url_update()      # Build the address
            self._payload_update()  # Payload info for request; from a string for sign
            self._sign()            # To sign the request by secret key
        else:
            self._update_headers()
            self._url_update()
            self._payload_update()
        return self._call_api()

    def _call_api(self):
        """
        Directly sending GET or POST request to an exchange depending on the method description from the dictionary
        :return: stock exchange response
        """
        method = self.methods[self.method]['method']
        response = requests.request(method=method, url=self.api_url, data=self.req_data, headers=self.headers, verify=True)
        if response.status_code == 200:
            return response.json()
        return {"code": "-1", "data": [{"sMsg": response.text}]}

    def get_balance(self, ccy=None, **kwargs):
        """
        Obtaining an asset balance from an exchange
        :param ccy: Instrument name (comma separated string, e.g. "BTC,ETH")
        :param kwargs:
        :return: result of api request
        """
        if ccy:
            kwargs.update({"ccy": ccy})
        self.payload = kwargs
        self.method = "account"
        return self._prepare()

    def create_order(self, instId=None, tdMode=None, side=None, ordType=None, sz=None, px=None, **kwargs):
        """
        https://www.okx.com/docs-v5/en/#rest-api-trade-place-order
        :return:
        """
        if instId:
            kwargs.update({"instId": instId})
        if tdMode:
            kwargs.update({"tdMode": tdMode})
        if side:
            kwargs.update({"side": side})
        if ordType:
            kwargs.update({"ordType": ordType})
        if sz:
            kwargs.update({"sz": sz})
        if px:
            kwargs.update({"px": px})
        self.payload = kwargs
        self.method = "create_order"
        return self._prepare()

    def cancel_order(self, instId=None, ordId=None, **kwargs):
        """
        https://www.okx.com/docs-v5/en/#rest-api-trade-cancel-order
        :return:
        """
        if instId:
            kwargs.update({"instId": instId})
        if ordId:
            kwargs.update({"ordId": ordId})
        self.payload = kwargs
        self.method = "cancel_order"
        return self._prepare()

    def orders_list(self, **kwargs):
        """
        https://www.okx.com/docs-v5/en/#rest-api-trade-get-order-list
        :return:
        """
        self.payload = kwargs
        self.method = "orders_info"
        return self._prepare()

    def order_info(self, instId=None, ordId=None, **kwargs):
        """
        https://www.okx.com/docs-v5/en/#rest-api-trade-get-order-details
        :return:
        """
        if instId:
            kwargs.update({"instId": instId})
        if ordId:
            kwargs.update({"ordId": ordId})
        self.payload = kwargs
        self.method = "order_info"
        return self._prepare()

    def get_positions(self, **kwargs):
        """
        https://www.okx.com/docs-v5/en/#rest-api-account-get-positions
        :return:
        """
        self.payload = kwargs
        self.method = "get_positions"
        return self._prepare()

    def candlesticks(self, instId=None, bar=None, limit=None, **kwargs):
        """
        https://www.okx.com/docs-v5/en/#rest-api-market-data-get-candlesticks
        :param instId:
        :param bar:
        :param limit:
        :param kwargs:
        :return:
        """
        if instId:
            kwargs.update({"instId": instId})
        if bar:
            kwargs.update({"bar": bar})
        if limit:
            kwargs.update({"limit": limit})
        self.method = "candlesticks"
        self.payload = kwargs
        return self._prepare()

    def tickers(self, inst_type, **kwargs):
        """
        https://www.okx.com/docs-v5/en/#rest-api-market-data-get-tickers
        :param inst_type:
        :param kwargs:
        :return:
        """
        if inst_type:
            kwargs.update({"instType": inst_type})
        self.method = "tickers"
        self.payload = kwargs
        return self._prepare()
