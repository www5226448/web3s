from web3s.module import (
    Module,
)
from web3s.utils.filters import (
    ShhFilter,
)


class Shh(Module):
    @property
    async def version(self):
        return await self.web3s.manager.request_blocking("shh_version", [])

    @property
    async def info(self):
        return await self.web3s.manager.request_blocking("shh_info", [])

    async def setMaxMessageSize(self, size):
        return await self.web3s.manager.request_blocking("shh_setMaxMessageSize", [size])

    async def setMinPoW(self, min_pow):
        return await self.web3s.manager.request_blocking("shh_setMinPoW", [min_pow])

    async def markTrustedPeer(self, enode):
        return await self.web3s.manager.request_blocking("shh_markTrustedPeer", [enode])

    async def newKeyPair(self):
        return await self.web3s.manager.request_blocking("shh_newKeyPair", [])

    async def addPrivateKey(self, key):
        return await self.web3s.manager.request_blocking("shh_addPrivateKey", [key])

    async def deleteKeyPair(self, id):
        return await self.web3s.manager.request_blocking("shh_deleteKeyPair", [id])

    async def hasKeyPair(self, id):
        return await self.web3s.manager.request_blocking("shh_hasKeyPair", [id])

    async def getPublicKey(self, id):
        return await self.web3s.manager.request_blocking("shh_getPublicKey", [id])

    async def getPrivateKey(self, id):
        return await self.web3s.manager.request_blocking("shh_getPrivateKey", [id])

    async def newSymKey(self):
        return await self.web3s.manager.request_blocking("shh_newSymKey", [])

    async def addSymKey(self, key):
        return await self.web3s.manager.request_blocking("shh_addSymKey", [key])

    async def generateSymKeyFromPassword(self, password):
        return await self.web3s.manager.request_blocking("shh_generateSymKeyFromPassword", [password])

    async def hasSymKey(self, id):
        return await self.web3s.manager.request_blocking("shh_hasSymKey", [id])

    async def getSymKey(self, id):
        return await self.web3s.manager.request_blocking("shh_getSymKey", [id])

    async def deleteSymKey(self, id):
        return await self.web3s.manager.request_blocking("shh_deleteSymKey", [id])

    async def post(self, message):
        if message and ("payload" in message):
            return await self.web3s.manager.request_blocking("shh_post", [message])
        else:
            raise ValueError(
                "message cannot be None or does not contain field 'payload'"
            )

    async def newMessageFilter(self, criteria, poll_interval=None):
        filter_id = self.web3s.manager.request_blocking("shh_newMessageFilter", [criteria])
        return await ShhFilter(self.web3s, filter_id, poll_interval=poll_interval)

    async def deleteMessageFilter(self, filter_id):
        return await self.web3s.manager.request_blocking("shh_deleteMessageFilter", [filter_id])

    async def getMessages(self, filter_id):
        return await self.web3s.manager.request_blocking("shh_getFilterMessages", [filter_id])
