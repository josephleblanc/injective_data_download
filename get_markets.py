from pyinjective.async_client import AsyncClient
from pyinjective.constant import Network
import asyncio
import csv

async def get_markets(market_status):
    # select network: local, testnet, mainnet
    network = Network.mainnet()
    client = AsyncClient(network, insecure=False)
    markets = await client.get_spot_markets(market_status=market_status)
    return markets

async def main():
    market_status = "active"
    header = [
            'market_id',
            'market_status',
            'ticker',
            'base_denom',
            'base_token_name',
            'base_token_address',
            'base_token_symbol',
            'base_token_logo',
            'base_token_decimals',
            'base_token_updated_at',
            'quote_denom',
            'quote_token_name',
            'quote_token_address',
            'quote_token_symbol',
            'quote_token_logo',
            'quote_token_decimals',
            'quote_token_updated_at',
            'maker_fee_rate',
            'taker_fee_rate',
            'service_provider_fee',
            'min_price_tick_size',
            'min_quantity_tick_size'
            ]
    with open('../datadir/markets/all_spot_active.csv', 'w') as markets_file:
        markets_writer = csv.writer(markets_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        markets_writer.writerow(header)
        markets = await get_markets(market_status)
        market_list = []
        for market in markets.markets:
            market_item = [
                market.market_id,
                market.market_status,
                market.ticker,
                market.base_denom,
                market.base_token_meta.name,
                market.base_token_meta.address,
                market.base_token_meta.symbol,
                market.base_token_meta.logo,
                market.base_token_meta.decimals,
                market.base_token_meta.updated_at,
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
                market.min_price_tick_size,
                market.min_quantity_tick_size
                ]
            market_list.append(market_item)
        markets_writer.writerows(market_list)

asyncio.run(main())
