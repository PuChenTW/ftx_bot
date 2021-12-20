from datetime import datetime
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


def write_log(msg, file_path: str = 'log.txt'):
    current = datetime.now().isoformat()
    with open(file_path, 'a') as f:
        f.write(f'[{current}] {msg}\n')


def update_lending(client: FtxClient, coin: str, preserve: float = 0, rate: float = None):
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
        try:
            update_lending(client, COIN, float(PRESERVE), float(RATE))
        except Exception as e:
            write_log(f'Error: {e}')
        else:
            write_log(f'Updated {COIN} lending')
    else:
        write_log('Detect offered size equal to 0, stop lending')
