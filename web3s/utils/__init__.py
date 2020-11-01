from asyncio import get_event_loop, gather
from typing import Coroutine, Any


def sync(coroutine: Coroutine) -> Any:
    loop = get_event_loop()
    result = loop.run_until_complete(coroutine)
    return result
