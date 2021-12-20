import hmac
from datetime import datetime
from requests import Request, Session, Response
from typing import Optional, Dict, Any, List
import urllib.parse
import time


class FtxClient:
    _ENDPOINT = 'https://ftx.com/api/'

    def __init__(self, api_key=None, api_secret=None, subaccount_name=None) -> None:
        self._session = Session()
        self._api_key = api_key
        self._api_secret = api_secret
        self._subaccount_name = subaccount_name

    @property
    def subaccount(self):
        return self._subaccount_name

    @subaccount.setter
    def subaccount(self, name):
        self._subaccount_name = name

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('GET', path, params=params)

    def _post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('POST', path, json=params)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self._ENDPOINT + path, **kwargs)
        self._sign_request(request)
        response = self._session.send(request.prepare())
        return self._process_response(response)

    def _sign_request(self, request: Request) -> None:
        ts = int(time.time() * 1000)
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode(
        )
        if prepared.body:
            signature_payload += prepared.body
        signature = hmac.new(self._api_secret.encode(),
                             signature_payload, 'sha256').hexdigest()
        request.headers['FTX-KEY'] = self._api_key
        request.headers['FTX-SIGN'] = signature
        request.headers['FTX-TS'] = str(ts)
        if self._subaccount_name:
            request.headers['FTX-SUBACCOUNT'] = urllib.parse.quote(
                self._subaccount_name)

    def _process_response(self, response: Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if not data['success']:
                raise Exception(data['error'])
            return data['result']

    def place_order(self, market: str, side: str, price: float, size: float, client_id: str,
                    type: str = 'limit', reduce_only: bool = False, ioc: bool = False, post_only: bool = False,
                    ) -> dict:
        return self._post('orders', {'market': market,
                                     'side': side,
                                     'price': price,
                                     'size': size,
                                     'type': type,
                                     'reduceOnly': reduce_only,
                                     'ioc': ioc,
                                     'postOnly': post_only,
                                     'clientId': client_id,
                                     })

    def get_open_orders(self, order_id: int, market: str = None) -> List[dict]:
        return self._get('orders', {'market': market, 'order_id': order_id})

    def get_lending_history(self, start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[dict]:
        params = {
            "start_time": int(datetime.strptime(start_time, '%Y%m%d').timestamp()) if start_time else None,
            "end_time": int(datetime.strptime(end_time, '%Y%m%d').timestamp()) if end_time else None
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._get('spot_margin/lending_history', params)

        def get_rate_and_apy(d): return {
            **d,
            "rate": f'{d["rate"] * 100} %',
            "apy": f'{d["rate"] * 24 * 365 * 100:.2f} %'
        }
        return list(map(get_rate_and_apy, response))

    def get_lending_rates(self, coin: str = None) -> List[dict]:
        response = self._get('spot_margin/lending_rates')
        if coin is None:
            return response

        def get_coin(d): return d['coin'].lower() == coin.lower()
        return list(filter(get_coin, response))

    def get_wallet_balances(self, coin: str = None) -> List[dict]:
        response = self._get('wallet/balances')
        if coin is None:
            return response

        def get_coin(d): return d['coin'].lower() == coin.lower()
        return list(filter(get_coin, response))

    def submit_lending_offer(self, coin: str, size: float, rate: float):
        return self._post('spot_margin/offers', {'coin': coin.upper(), 'size': size, 'rate': rate})

    def get_spot_margin_lending_info(self, coin: str = None):
        response = self._get('spot_margin/lending_info')
        if coin is None:
            return response

        def get_coin(d): return d['coin'].lower() == coin.lower()
        return list(filter(get_coin, response))

    def get_all_subaccounts(self):
        return self._get('subaccounts')

    def get_all_wallet_balances(self):
        self.subaccount = None
        balances = [['Main_account', self.get_wallet_balances()]]
        for subaccount in self.get_all_subaccounts():
            self.subaccount = subaccount['nickname']
            balances.append(
                [subaccount['nickname'], self.get_wallet_balances()])
        return balances
