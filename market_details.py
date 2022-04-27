from pyinjective.async_client import AsyncClient
from pyinjective.constant import Network
import asyncio

async def main() -> None:
    # select network: local, testnet, mainnet
    network = Network.mainnet()
    client = AsyncClient(network, insecure=False)
    market_id = "0x01e920e081b6f3b2e5183399d5b6733bb6f80319e6be3805b95cb7236910ff0e"
    market = await client.get_spot_market(market_id=market_id)
    print(market)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
