from pyinjective.async_client import AsyncClient
from pyinjective.constant import Network
import asyncio

async def main() -> None:
    # select network: local, testnet, mainnet
    network = Network.mainnet()
    client = AsyncClient(network, insecure=False)
    market_id = "0xa508cb32923323679f29a032c70342c147c17d0145625922b0ef22e955c844c0"
    print('before awaiting the client')
    trades = await client.stream_spot_trades(market_id=market_id)
    print('after awaiting on client')

    async for trade in trades:
        print(trade)

asyncio.run(main())
