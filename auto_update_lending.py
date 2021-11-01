import os
import math
from ftx_client import client
from dotenv import load_dotenv
load_dotenv()

SUB_ACCOUNT = os.getenv('SUB_ACCOUNT')
COIN = os.getenv('LEND_COIN')


def update_lending(coin, preserve: float = 0, rate: float = None):
    lendable = client.get_spot_margin_lending_info(coin)[0]['lendable']
    intrest = rate if rate is not None else client.get_lending_rates(coin)[
        0]['estimate']
    size = math.floor((lendable - preserve) * 1000000) / 1000000
    return client.submit_lending_offer(coin, size, intrest)


if __name__ == '__main__':
    client.subaccount = os.getenv(SUB_ACCOUNT)
    update_lending(COIN)
