import httpx
from common.config import load_config
import asyncio

config = load_config()


async def test_proxy():
    http_client = httpx.AsyncClient(proxies=config.proxy)
    response = await http_client.get('https://api.ipify.org')
    print(f"IP через прокси: {response.text}")


asyncio.run(test_proxy())
