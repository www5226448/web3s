
import sys


if sys.version_info < (3, 5):
    raise EnvironmentError("Python 3.5 or above is required")

from eth_account import Account  # noqa: E402
from web3s.main import Web3s  # noqa: E402
from web3s.providers.rpc import (  # noqa: E402
    HTTPProvider,
)
from web3s.providers.eth_tester import (  # noqa: E402
    EthereumTesterProvider,
)
from web3s.providers.tester import (  # noqa: E402
    TestRPCProvider,
)

__version__ ='4.9.0'

__all__ = [
    "__version__",
    "Web3s",
    "HTTPProvider",

    "TestRPCProvider",
    "EthereumTesterProvider",
    "Account",
]
