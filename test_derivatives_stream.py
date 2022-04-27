from pyinjective.async_client import AsyncClient
from pyinjective.constant import Network
import asyncio
import csv

async def listener(q: asyncio.Queue) -> None:
    # set up client for listener used at the end of listener()
    network = Network.mainnet()
    client = AsyncClient(network, insecure=False)
    markets_csv_filepath = '../datadir/markets/all_derivatives_active.csv'

    # Read market_ids and tickers from a csv file, which is created in another
    # function get_all_markets.py
    market_ids = []
    market_info = {}
    with open(markets_csv_filepath, 'r') as markets_csv:
        reader = csv.reader(markets_csv, delimiter=',', quotechar='"')
        for row in reader:
            market_ids.append(row[0])
            market_info[row[0]] = row[2]

    # Remove headers from list and dict
    del market_ids[0]
    market_info.pop('market_id')

    # Filepath dict used for to identify the ticker name of a streamed trade,
    # since the ticker is not included in the streaming response
    filepath_dict = {}

    # Initialize csv files for where saved trades will go
    for entry in market_ids:
        filename = f'{market_info[entry]}_stream.csv'.replace('/', '-', 1).replace(' ', '_', 1)
        filepath = f'../datadir/derivatives_stream/{filename}'
        filepath_dict[entry] = filepath
        with open(filepath, 'w') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quotechar='"', \
                    quoting=csv.QUOTE_MINIMAL)
            header = ([
                'order_hash',
                'subaccount_id',
                'market_id',
                'trade_execution_type',
                'position_delta.trade_direction',
                'position_delta.execution_price',
                'position_delta.execution_quantity',
                'position_delta.execution_margin',
                'payout',
                'fee',
                'executed_at'
                ])
            writer.writerow(header)
    
    # This is just a check to make sure the market_ids and market_info are
    # being read correctly
    print('market_ids:', market_ids)
    print('market_info:', market_info)

    # The actual listener, sends trades to queue as they arrive, along with
    # the information needed to save the data in the correct place.
    trades = await client.stream_derivative_trades(market_ids=market_ids)
    async for trade in trades:
        await q.put([trade, \
                market_info[trade.trade.market_id], \
                filepath_dict[trade.trade.market_id]])

async def printer(q: asyncio.Queue) -> None:
    # Forever loop continues to await on queue as the listener function waits
    # for more responses.
    while True:
        t, ticker, filepath = await q.get()
        # Unnecessary prints used for a sanity check
        print('task received')
        print(f't:\n{t}')
        # Uses filepath and ticker identified at end of listener()
        with open(filepath, 'a') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quotechar='"', \
                    quoting=csv.QUOTE_MINIMAL)
            writer.writerow([
                t.trade.order_hash,
                t.trade.subaccount_id,
                t.trade.market_id,
                t.trade.trade_execution_type,
                t.trade.position_delta.trade_direction,
                t.trade.position_delta.execution_price,
                t.trade.position_delta.execution_quantity,
                t.trade.position_delta.execution_margin,
                t.trade.payout,
                t.trade.fee,
                t.trade.executed_at
                ])
        # Sanity check to make sure write completed
        print(f'ticker: {ticker}\n')
        q.task_done()

async def main() -> None:
    # Set up for functions to run using async queue.
    q = asyncio.Queue()
    streaming_markets = [asyncio.create_task(listener(q))]
    consumers = [asyncio.create_task(printer(q))]
    await asyncio.gather(*streaming_markets)
    await q.join()
    for c in consumers:
        c.cancel()

asyncio.run(main())
