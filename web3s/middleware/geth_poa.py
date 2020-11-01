from eth_utils.curried import (
    apply_formatters_to_dict,
    apply_key_map,
)
from hexbytes import (
    HexBytes,
)

from web3s.middleware.formatting import (
    construct_formatting_middleware,
)
from web3s.utils.toolz import (
    compose,
)

remap_geth_poa_fields = apply_key_map({
    'extraData': 'proofOfAuthorityData',
})

pythonic_geth_poa = apply_formatters_to_dict({
    'proofOfAuthorityData': HexBytes,
})

geth_poa_cleanup = compose(pythonic_geth_poa, remap_geth_poa_fields)

geth_poa_middleware = construct_formatting_middleware(
    result_formatters={
        'eth_getBlockByHash': geth_poa_cleanup,
        'eth_getBlockByNumber': geth_poa_cleanup,
    },
)
