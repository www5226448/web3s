from typing import (
    Any,
)

from eth_typing import (
    URI,
)

import json

import aiohttp




async def make_post_request(endpoint_uri: URI, data: bytes, *args: Any, **kwargs: Any) -> bytes:

    async with aiohttp.ClientSession(*args,**kwargs) as session:
        data=json.loads(data)
        async with session.post(endpoint_uri, json=data) as resp:
            resp.raise_for_status()
            response=await resp.read()

            return response

