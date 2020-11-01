from web3s.module import (
    Module,
)


class Admin(Module):
    async def addPeer(self, node_url):
        return await self.web3s.manager.request_blocking(
            "admin_addPeer", [node_url],
        )

    @property
    async def datadir(self):
        return await self.web3s.manager.request_blocking("admin_datadir", [])

    @property
    async def nodeInfo(self):
        return await self.web3s.manager.request_blocking("admin_nodeInfo", [])

    @property
    async def peers(self):
        return await self.web3s.manager.request_blocking("admin_peers", [])

    async def setSolc(self, solc_path):
        return await self.web3s.manager.request_blocking(
            "admin_setSolc", [solc_path],
        )

    async def startRPC(self, host='localhost', port='8545', cors="", apis="eth,net,web3s"):
        return await self.web3s.manager.request_blocking(
            "admin_startRPC",
            [host, port, cors, apis],
        )

    async def startWS(self, host='localhost', port='8546', cors="", apis="eth,net,web3s"):
        return await self.web3s.manager.request_blocking(
            "admin_startWS",
            [host, port, cors, apis],
        )

    async def stopRPC(self):
        return await self.web3s.manager.request_blocking("admin_stopRPC", [])

    async def stopWS(self):
        return await self.web3s.manager.request_blocking("admin_stopWS", [])
