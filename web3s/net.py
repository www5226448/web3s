from web3s.module import (
    Module,
)


class Net(Module):
    @property
    async def listening(self):
        return await self.web3s.manager.request_blocking("net_listening", [])

    @property
    async def peerCount(self):
        return await self.web3s.manager.request_blocking("net_peerCount", [])

    @property
    async def chainId(self):
        result = await self.web3s.manager.request_blocking("eth_chainId", [])
        return int(result, base=16)

    @property
    async def version(self):
        return await self.web3s.manager.request_blocking("net_version", [])
