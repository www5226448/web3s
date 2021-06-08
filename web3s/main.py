from eth_utils import (
    apply_to_return_value,
    add_0x_prefix,
    from_wei,
    is_address,
    is_checksum_address,
    keccak,
    remove_0x_prefix,
    to_checksum_address,
    to_wei,
)



from web3s.admin import Admin
from web3s.eth import Eth
from web3s.iban import Iban
from web3s.miner import Miner
from web3s.net import Net
from web3s.parity import Parity
from web3s.personal import Personal
from web3s.testing import Testing
from web3s.txpool import TxPool
from web3s.version import Version

from web3s.providers.eth_tester import (
    EthereumTesterProvider,
)

from web3s.providers.rpc import (
    HTTPProvider,
)
from web3s.providers.tester import (
    TestRPCProvider,
)

from web3s.manager import (
    RequestManager,
)

from web3s.utils.abi import (
    map_abi_data,
)
from hexbytes import (
    HexBytes,
)
from web3s.utils.decorators import (
    combomethod,
)
from web3s.utils.empty import empty
from web3s.utils.encoding import (
    hex_encode_abi_type,
    to_bytes,
    to_int,
    to_hex,
    to_text,
)



from web3s.utils.decorators import async_apply_to_return_value


def get_default_modules():
    return {
        "eth": Eth,
        "net": Net,
        "personal": Personal,
        "version": Version,
        "txpool": TxPool,
        "miner": Miner,
        "admin": Admin,
        "parity": Parity,
        "testing": Testing,
    }


class Web3s:
    # Providers
    HTTPProvider = HTTPProvider

    TestRPCProvider = TestRPCProvider
    EthereumTesterProvider = EthereumTesterProvider


    # Managers
    RequestManager = RequestManager

    # Iban
    Iban = Iban

    # Encoding and Decoding
    toBytes = staticmethod(to_bytes)
    toInt = staticmethod(to_int)
    toHex = staticmethod(to_hex)
    toText = staticmethod(to_text)

    # Currency Utility
    toWei = staticmethod(to_wei)
    fromWei = staticmethod(from_wei)

    # Address Utility
    isAddress = staticmethod(is_address)
    isChecksumAddress = staticmethod(is_checksum_address)
    toChecksumAddress = staticmethod(to_checksum_address)


    def __init__(self, providers=empty, middlewares=None, modules=None):
        self.manager = RequestManager(self, providers, middlewares)

        if modules is None:
            modules = get_default_modules()

        for module_name, module_class in modules.items():
            module_class.attach(self, module_name)


        self.contracts={}

    @property
    def middleware_stack(self):
        return self.manager.middleware_stack

    @property
    def providers(self):
        return self.manager.providers

    @providers.setter
    def providers(self, providers):
        self.manager.providers = providers

    @staticmethod
    @apply_to_return_value(HexBytes)
    def sha3(primitive=None, text=None, hexstr=None):
        if isinstance(primitive, (bytes, int, type(None))):
            input_bytes = to_bytes(primitive, hexstr=hexstr, text=text)
            return keccak(input_bytes)

        raise TypeError(
            "You called sha3 with first arg %r and keywords %r. You must call it with one of "
            "these approaches: sha3(text='txt'), sha3(hexstr='0x747874'), "
            "sha3(b'\\x74\\x78\\x74'), or sha3(0x747874)." % (
                primitive,
                {'text': text, 'hexstr': hexstr}
            )
        )


    async def isConnected(self):
        for provider in self.providers:
            if await provider.isConnected():
                return True
        else:
            return False


