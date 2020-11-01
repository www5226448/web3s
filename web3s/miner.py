from web3s.module import (
    Module,
)


class Miner(Module):
    @property
    async def hashrate(self):
        return await self.web3s.manager.request_blocking("eth_hashrate", [])

    async def makeDAG(self, number):
        return await self.web3s.manager.request_blocking("miner_makeDag", [number])

    async def setExtra(self, extra):
        return await self.web3s.manager.request_blocking("miner_setExtra", [extra])

    async def setEtherBase(self, etherbase):
        return await self.web3s.manager.request_blocking("miner_setEtherbase", [etherbase])

    async def setGasPrice(self, gas_price):
        return await self.web3s.manager.request_blocking(
            "miner_setGasPrice", [gas_price],
        )

    async def start(self, num_threads):
        return await self.web3s.manager.request_blocking(
            "miner_start", [num_threads],
        )

    async def stop(self):
        return await self.web3s.manager.request_blocking("miner_stop", [])

    async def startAutoDAG(self):
        return await self.web3s.manager.request_blocking("miner_startAutoDag", [])

    async def stopAutoDAG(self):
        return await self.web3s.manager.request_blocking("miner_stopAutoDag", [])
