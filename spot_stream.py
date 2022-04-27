# Interesting possible things to do
# - Grabbing all the trades since the program last ran with another function and
#   add them to the current file before continuing to run to have complete
#   historical data since the program was first run.

from pyinjective.async_client import AsyncClient
from pyinjective.constant import Network
from os.path import exists
import asyncio
import csv

async def main():
    network = Network.mainnet()
    client = AsyncClient(network, insecure=False)
    # markets_list is of the form [[market_id, ticker], [..] .. ]
    markets_list = []
    with open('../datadir/markets/all_active.csv', 'r') as markets_file:
        reader = csv.reader(markets_file, delimiter=',', quotechar='"')
        for row in reader:
            markets_list.append([row[0], row[2]])
    
    # Delete the header of the file from the list
    del markets_list[0]

    # Turn market_list into a tuple so it can be used in the python thing that
    # constructs lists.
    markets_list = tuple(markets_list)
    for market_info in markets_list:
        print(market_info)
        create_market_file(market_info)

    print(f"market_list[1]: {markets_list[1]}")

    q = asyncio.Queue()
    streaming_markets = [asyncio.create_task(listen_stream_trade(q, market_info, client)) for market_info in markets_list]
    consumers = [asyncio.create_task(append_trade_to_file(q))]
    await asyncio.gather(*streaming_markets)
    await q.join()
    # Honesty I haven no idea what this does and should probably find out.
    for c in consumers:
        c.cancel()

# Creates and initializes the header for the .csv files where the streamed
# trades are all going to be appended.
def create_market_file(market_info):
    market_id, ticker = market_info[0], market_info[1]
    formatted_file_path = '../datadir/trades/{}_stream_trades.csv'.format('{}'.format(ticker).replace('/', '-', 1))
    with open(formatted_file_path, 'w') as market_trades:
        writer = csv.writer(market_trades, delimiter=',', quotechar='"', \
                quoting=csv.QUOTE_MINIMAL)
        writer.writerow([
            'operation_type',
            'timestamp',
            'trade',
            'executed_at',
            'fee',
            'market_id',
            'order_hash',
            'price',
            'quantity',
            'timestamp',
            'subaccount_id',
            'trade_direction',
            'trade_execution_type',
            'fee_recipient'
            ])

# Listens for new trades on the given market and puts them on the queue to be 
# written to file in another function, along with the info on where they are
# going to be saved.
# This runs in a forever loop
async def listen_stream_trade(q: asyncio.Queue, market_info, client):
    while True:
        market_id, ticker = market_info[0], market_info[1]
        formatted_file_path = '../datadir/trades/{}_stream_trades.csv'.format('{}'.format(ticker).replace('/', '-', 1))
#        print(f"Listening for {ticker}")
        print(f"market_id: {market_id}")
        trades = await client.stream_spot_trades(market_id=market_id)
        async for trade in trades:
            q.put((market_id, ticker, trade))
            print(f'q.qsize(): {q.qsize()}')
        print(f'{ticker} is going to sleep')
        asyncio.sleep(5)
#    print(f"{ticker} put")

# awaits on q.get() for new trades from all the markets to be put into the
# queue, then writes them to the file corresponding to their ticker.
# The forever loop works here because it awaits on q.get()
async def append_trade_to_file(q: asyncio.Queue):
    while True:
        print('activating consumer')
        print('before q.get() activates')
        market_id, ticker, resp = await q.get()
        something = await resp
        print(f'something: {something}')
        print('after q.get() activates')
        print(f'market_id: {market_id}\nticker: {ticker}\nresp: {resp}')
        print(resp.trade)
        formatted_file_path = '../datadir/trades/{}_stream_trades.csv'.format('{}'.format(ticker).replace('/', '-', 1))
        with open(formatted_file_path, 'a') as trades_file:
            writer = csv.writer(trades_file, delimiter=',', quotechar='"', \
                    quoting=csv.QUOTE_MINIMAL)
            print(resp.timestamp, ticker)
            print(resp)
            writer.writerow([
                resp.operation_type,
                resp.timestamp,
                resp.trade.executed_at,
                resp.trade.fee,
                resp.trade.market_id,
                resp.trade.order_hash,
                resp.trade.price.price,
                resp.trade.price.quantity,
                resp.trade.price.timestamp,
                resp.trade.subaccount_id,
                resp.trade.trade_direction,
                resp.trade.trade_execution_type,
                resp.trade.fee_recipient,
                ])
        q.task_done()

asyncio.run(main())
