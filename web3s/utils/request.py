import asyncio

from typing import (
    Any
)


from eth_typing import (
    URI,
)
import asyncio
import json

import lru

from aiohttp import ClientSession
from web3s.utils.caching import (
    generate_cache_key,
)




def cache_session(endpoint_uri: URI, session: ClientSession) -> None:
    cache_key = generate_cache_key(endpoint_uri)
    _session_cache[cache_key] = session

async def _remove_session(key: str, session: ClientSession) -> None:
    await session.close()

def __remove_session(key: str, session: ClientSession) -> None:
    print('remove session')
    try:
        asyncio.ensure_future(remove_session(key, session))
    except AttributeError:
        asyncio.create_task(remove_session(key, session))



_session_cache = lru.LRU(9, callback=__remove_session)


def _get_session(endpoint_uri: URI) -> ClientSession:
    cache_key = generate_cache_key(endpoint_uri)
    if cache_key not in _session_cache:
        _session_cache[cache_key] = ClientSession()
    return _session_cache[cache_key]





async def make_post_request(endpoint_uri: URI, data: bytes, *args: Any, **kwargs: Any) -> bytes:
    session = _get_session(endpoint_uri)


    data=json.loads(data)
    response=await session.post(endpoint_uri, json=data)
    response.raise_for_status()

    async with response as resp:
        result=await resp.read()
    return result

