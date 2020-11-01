from web3s.module import (
    Module,
)


class TxPool(Module):
    @property
    async def content(self):

        tx_pool=await self.web3s.manager.request_blocking("txpool_content", [])

        return tx_pool


    async def inspect(self):
        return await self.web3s.manager.request_blocking("txpool_inspect", [])

    @property
    async def status(self):
        return await self.web3s.manager.request_blocking("txpool_status", [])
