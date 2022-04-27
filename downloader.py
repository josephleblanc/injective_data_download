from pyinjective.async_client import AsyncClient
from pyinjective.constant import Network
import asyncio
import csv

async def download(market_id, limit=None, skip=None):
    # select network: local, testnet, mainnet
    network = Network.mainnet()
    client = AsyncClient(network, insecure=False)
    orders = await client.get_spot_trades(market_id=market_id, limit=limit, skip=skip)
    return orders

async def main() -> None:
    market_id = "0x01e920e081b6f3b2e5183399d5b6733bb6f80319e6be3805b95cb7236910ff0e"
    limit = 100
    with open('../datadir/trades/{}.csv'.format(market_id), mode='w') as trades_file:
        trades_writer = csv.writer(trades_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        trades_writer.writerow([
            'order_hash',
            'subaccount_id',
            'market_id',
            'trade_execution_type',
            'trade_direction',
            'price',
            'quantity',
            'timestamp',
            'fee',
            'execution_at'
            ])
        for skip in range(0, 1000, 100):
            order = await download(market_id, limit=limit, skip=skip)
            print(skip)
            for trade in order.trades:
                trades_writer.writerow([
                    trade.order_hash,
                    trade.subaccount_id,
                    trade.market_id,
                    trade.trade_execution_type,
                    trade.trade_direction,
                    trade.price.price,
                    trade.price.quantity,
                    trade.price.timestamp,
                    trade.fee,
                    trade.executed_at
                    ])

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
