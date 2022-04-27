from pyinjective.async_client import AsyncClient
from pyinjective.constant import Network
import asyncio
import csv

async def get_markets(market_status) -> None:
    # select network: local, testnet, mainnet
    network = Network.mainnet()
    client = AsyncClient(network, insecure=False)
    markets = await client.get_derivative_markets(market_status=market_status)
    return markets

async def main():
    market_status = "active"
    header = [
            'market_id',
            'market_status',
            'ticker',
            'oracle_base',
            'oracle_quote',
            'oracle_type',
            # Taking this out just because it is annoying to deal with and
            # I don't need it for anything
            #'oracle_scaling_factor',
            'initial_margin_ratio',
            'maintenance_margin_ratio',
            'quote_denom',
            'quote_token_meta_name',
            'quote_token_meta_address',
            'quote_token_meta_symbol',
            'quote_token_meta_logo',
            'quote_token_meta_decimals',
            'quote_token_meta_updated_at',
            'maker_fee_rate',
            'taker_fee_rate',
            'service_provider_fee',
            'is_perpetual',
            'min_price_tick_size',
            'min_quantity_tick_size',
            'perpetual_market_info_hourly_funding_rate_cap',
            'perpetual_market_info_hourly_interest_rate',
            'perpetual_market_info_next_funding_timestamp',
            'perpetual_market_info_funding_interval',
            'perpetual_market_funding_cumulative_funding',
            'perpetual_market_funding_cumulative_price',
            'perpetual_market_funding_last_timestamp'
            ]
    with open('../datadir/markets/all_derivatives_active.csv', 'w') as markets_file:
        markets_writer = csv.writer(markets_file, delimiter=',', quotechar='"', \
                quoting=csv.QUOTE_MINIMAL)
        markets_writer.writerow(header)
        markets = await get_markets(market_status)
        market_list = []
        for market in markets.markets:
            print(market)
            market_item = [
                market.market_id,
                market.market_status,
                market.ticker,
                market.oracle_base,
                market.oracle_quote,
                market.oracle_type,
                # Taking this out because it is annoying. Its cast as an int while
                # literally everything else is a string. And I don't even know what
                # it is for or what it does.
                # str(market.oracle_scaling_factor),
                market.initial_margin_ratio,
                market.maintenance_margin_ratio,
                market.quote_denom,
                market.quote_token_meta.name,
                market.quote_token_meta.address,
                market.quote_token_meta.symbol,
                market.quote_token_meta.logo,
                market.quote_token_meta.decimals,
                market.quote_token_meta.updated_at,
                market.maker_fee_rate,
                market.taker_fee_rate,
                market.service_provider_fee,
                market.is_perpetual,
                market.min_price_tick_size,
                market.min_quantity_tick_size,
                market.perpetual_market_info.hourly_funding_rate_cap,
                market.perpetual_market_info.hourly_interest_rate,
                market.perpetual_market_info.next_funding_timestamp,
                market.perpetual_market_info.funding_interval,
                market.perpetual_market_funding.cumulative_funding,
                market.perpetual_market_funding.cumulative_price,
                market.perpetual_market_funding.last_timestamp
                ]
            market_list.append(market_item)
        markets_writer.writerows(market_list)

asyncio.run(main())
