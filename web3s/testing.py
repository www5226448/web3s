from web3s.module import (
    Module,
)


class Testing(Module):
    async def timeTravel(self, timestamp):
        return await self.web3s.manager.request_blocking("testing_timeTravel", [timestamp])

    async def mine(self, num_blocks=1):
        return await self.web3s.manager.request_blocking("evm_mine", [num_blocks])

    async def snapshot(self):
        self.last_snapshot_idx = await self.web3s.manager.request_blocking("evm_snapshot", [])
        return self.last_snapshot_idx

    async def reset(self):
        return await self.web3s.manager.request_blocking("evm_reset", [])

    async def revert(self, snapshot_idx=None):
        if snapshot_idx is None:
            revert_target = self.last_snapshot_idx
        else:
            revert_target = snapshot_idx
        return await self.web3s.manager.request_blocking("evm_revert", [revert_target])
