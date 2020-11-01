from web3s.module import (
    Module,
)


class Version(Module):
    @property
    def api(self):
        from web3s import __version__
        return __version__

    @property
    async def node(self):
        return await self.web3s.manager.request_blocking("web3_clientVersion", [])

    @property
    async def network(self):
        return await self.web3s.manager.request_blocking("net_version", [])

    @property
    async def ethereum(self):
        return await self.web3s.manager.request_blocking("eth_protocolVersion", [])
