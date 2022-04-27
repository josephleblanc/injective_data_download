from pyinjective.async_client import AsyncClient
from pyinjective.constant import Network
import asyncio

async def listen(q: asyncio.Queue()) -> None:
    network = Network.mainnet()
    client = AsyncClient(network, insecure=False)
    market_id = "0xa508cb32923323679f29a032c70342c147c17d0145625922b0ef22e955c844c0"
    print('before awaiting on clinet')
    orders = await client.stream_spot_orders(market_id=market_id)
    print('after awaiting on clinet')

    async for order in orders:
        print('inside loop')
        await q.put(order)
        print('after q.put(order)')
    print('how did we get here? i guess its time to wait a bit')
    await asyncio.sleep(.5)

async def printer(q: asyncio.Queue()) -> None:
    print('inside printer')
    while True:
        print('\t inside printer loop')
        to_print = await q.get()
        print('\t after awaiting q.get()')
        print(to_print)
        q.task_done()

async def main() -> None:
    q = asyncio.Queue()
    producer = asyncio.create_task(listen(q))
    consumer = asyncio.create_task(printer(q))
    await asyncio.gather(producer)
    await q.join()
    printer.cancel()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
