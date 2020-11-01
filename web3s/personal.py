from web3s.module import (
    Module,
)


class Personal(Module):
    """
    https://github.com/ethereum/go-ethereum/wiki/Management-APIs#personal
    """
    async def importRawKey(self, private_key, passphrase):
        return await self.web3s.manager.request_blocking(
            "personal_importRawKey",
            [private_key, passphrase],
        )

    async def newAccount(self, password):
        return await self.web3s.manager.request_blocking(
            "personal_newAccount", [password],
        )

    @property
    async def listAccounts(self):
        return await self.web3s.manager.request_blocking(
            "personal_listAccounts", [],
        )

    async def sendTransaction(self, transaction, passphrase):
        return await self.web3s.manager.request_blocking(
            "personal_sendTransaction",
            [transaction, passphrase],
        )

    async def lockAccount(self, account):
        return await self.web3s.manager.request_blocking(
            "personal_lockAccount",
            [account],
        )

    async def unlockAccount(self, account, passphrase, duration=None):
        try:
            return await self.web3s.manager.request_blocking(
                "personal_unlockAccount",
                [account, passphrase, duration],
            )
        except ValueError as err:
            if "could not decrypt" in str(err):
                # Hack to handle go-ethereum error response.
                return False
            else:
                raise

    async def sign(self, message, signer, passphrase):
        return await self.web3s.manager.request_blocking(
            'personal_sign',
            [message, signer, passphrase],
        )

    async def ecRecover(self, message, signature):
        return await self.web3s.manager.request_blocking(
            'personal_ecRecover',
            [message, signature],
        )
