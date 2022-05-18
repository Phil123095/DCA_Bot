import DCA_Bot as ft
import os
import dotenv
import krakenex
from pykrakenapi import KrakenAPI


def lambda_handler(event, context):
    if os.environ.get("AWS_EXECUTION_ENV") is None:
        dotenv.load_dotenv()

    api = krakenex.API(key=os.environ['API_KEY'],
                       secret=os.environ['API_SECRET'])
    k = KrakenAPI(api)

    pair_combinations = {'CHF': {'BTC': 'XBTCHF', 'ETH': 'ETHCHF'}, 'ZEUR': {'BTC': 'XBTEUR', 'ETH': 'ETHEUR'}}

    ft.trade_orchestrator(kraken=k, pair_combinations=pair_combinations, asset_to_buy='BTC',
                          DCA_percentage=0.1)

    return

