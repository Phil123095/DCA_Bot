from time import sleep
import os
import dotenv
import krakenex
from pykrakenapi import KrakenAPI
import pandas as pd


def get_last_funding_amount(kraken):
    trial = kraken.get_ledgers_info(type="deposit", asset='ZEUR, CHF')

    trial_table = trial[0]
    deposits_only = trial_table[trial_table['type'] == 'deposit']
    deposits_only = deposits_only[(deposits_only['asset'] == 'CHF') | (deposits_only['asset'] == 'ZEUR')]
    deposits_only.sort_values(by="time", ascending=False)
    last_deposit = deposits_only.iloc[0]
    currency_class, amount = last_deposit['asset'], last_deposit['balance']

    return currency_class, amount


def calculate_money_to_spend(initial_funding, DCA_perc, current_balance):
    amount_to_spend = initial_funding * DCA_perc

    if amount_to_spend <= current_balance:
        return amount_to_spend
    else:
        return 0


def calculate_crypto_amount_to_buy(kraken, currency_pair, amount_to_spend):
    crypto = kraken.get_ticker_information(currency_pair)
    crypto_price = float(crypto['a'][0][0])
    crypto_higher_price = crypto_price + 2

    actual_available_amount_to_spend = float(amount_to_spend/1.015)

    volume = actual_available_amount_to_spend/crypto_higher_price
    print(volume)
    return crypto_higher_price, volume


def get_current_account_balance(kraken):
    balances = kraken.get_account_balance()

    try:
        CHF_holdings = balances.loc['CHF']['vol']
    except KeyError:
        CHF_holdings = 0

    try:
        EUR_holdings = balances.loc['ZEUR']['vol']
    except KeyError:
        EUR_holdings = 0

    return CHF_holdings, EUR_holdings


def execute_trade_order(kraken, currency_pair, volume, ask_amount):

    response = kraken.add_standard_order(pair=currency_pair, type='buy', ordertype='limit',
                                         volume=volume, price=ask_amount, validate=False)

    sleep(3)

    check_order = k.query_orders_info(response['txid'][0])

    if check_order['status'][0] == 'open' or 'closed':
        print('Order completed sucessfully')

    else:
        print('Order rejected')


def trade_orchestrator(kraken, pair_combinations, asset_to_buy, DCA_percentage):

    CHF_holdings, EUR_holdings = get_current_account_balance(kraken=kraken)
    print(CHF_holdings, EUR_holdings)

    if CHF_holdings > 10 or EUR_holdings > 10:
        currency_class, total_funding_amount = get_last_funding_amount(kraken=kraken)

        if currency_class == 'CHF':
            final_currency_amount = CHF_holdings

        else:
            final_currency_amount = EUR_holdings

        asset_pair_buy = pair_combinations[currency_class][asset_to_buy]

        amount_to_spend = calculate_money_to_spend(initial_funding=total_funding_amount, DCA_perc=DCA_percentage,
                                                   current_balance=final_currency_amount)
        print(f"Amount to spend: {amount_to_spend}")

        if amount_to_spend > 0:
            ask_price, crypto_volume = calculate_crypto_amount_to_buy(kraken=kraken, currency_pair=asset_pair_buy,
                                                                      amount_to_spend=amount_to_spend)
            print(f"Ask Price: {ask_price} @ {crypto_volume} BTC")

            execute_trade_order(kraken=kraken, currency_pair=asset_pair_buy, volume=crypto_volume, ask_amount=ask_price)

        else:
            print("Insufficient amount to buy")

    else:
        print("No funds to do DCA with")

    return

