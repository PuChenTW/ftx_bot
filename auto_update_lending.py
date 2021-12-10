import os
import math
from ftx_client import FtxClient
from dotenv import load_dotenv
load_dotenv()

SUB_ACCOUNT = os.getenv('SUB_ACCOUNT')
COIN = os.getenv('LEND_COIN')
KEY = os.getenv('KEY')
SECRET = os.getenv('SECRET')
PRESERVE = os.getenv('PRESERVE', 0)
RATE = os.getenv('RATE', 0)


def update_lending(coin, preserve: float = 0, rate: float = None):
    lendable = client.get_spot_margin_lending_info(coin)[0]['lendable']
    intrest = rate if rate is not None else client.get_lending_rates(coin)[
        0]['estimate']
    size = math.floor((lendable - preserve) * 1000000) / 1000000
    return client.submit_lending_offer(coin, size, intrest)


if __name__ == '__main__':
    client = FtxClient(api_key=KEY, api_secret=SECRET)
    client.subaccount = SUB_ACCOUNT
    if SUB_ACCOUNT is None:
        SUB_ACCOUNT = input('Subaccount: ')
    if not PRESERVE:
        PRESERVE = input('Preserve: ')
    if not RATE:
        RATE = input('Minimum rate: ')

    offered = client.get_spot_margin_lending_info(COIN)[0].get('offered')
    if offered > 0:
        update_lending(COIN, float(PRESERVE), float(RATE))
    else:
        print('Detect offered size equal to 0, stop lending')
