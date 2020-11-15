from eth_account import (
    Account,
)
from eth_utils import (
    apply_to_return_value,
    is_checksum_address,
    is_string,
    to_checksum_address,
)
from hexbytes import (
    HexBytes,
)

from web3s.contract import (
    Contract,
)
from web3s.iban import (
    Iban,
)
from web3s.module import (
    Module,
)
from web3s.utils.blocks import (
    select_method_for_block_identifier,
)
from web3s.utils.decorators import (
    deprecated_for,
)
from web3s.utils.empty import (
    empty,
)
from web3s.utils.encoding import (
    to_hex,
)
from web3s.utils.filters import (
    BlockFilter,
    LogFilter,
    TransactionFilter,
)
from web3s.utils.toolz import (
    assoc,
    merge,
)
from web3s.utils.transactions import (
    assert_valid_transaction_params,
    extract_valid_transaction_params,
    get_buffered_gas_estimate,
    get_required_transaction,
    replace_transaction,
    wait_for_transaction_receipt,
)

from web3s.utils.decorators import async_apply_to_return_value





class Eth(Module):
    account = Account()
    defaultAccount = empty
    defaultBlock = "latest"
    defaultContractFactory = Contract
    iban = Iban
    gasPriceStrategy = None




    @deprecated_for("doing nothing at all")
    def enable_unaudited_features(self):
        pass

    def namereg(self):
        raise NotImplementedError()

    def icapNamereg(self):
        raise NotImplementedError()

    @property
    async def protocolVersion(self):
        return await self.web3s.manager.request_blocking("eth_protocolVersion", [])

    @property
    async def syncing(self):
        return await self.web3s.manager.request_blocking("eth_syncing", [])

    @property
    async def coinbase(self):
        return await self.web3s.manager.request_blocking("eth_coinbase", [])

    @property
    async def mining(self):
        return await self.web3s.manager.request_blocking("eth_mining", [])

    @property
    async def hashrate(self):
        return await self.web3s.manager.request_blocking("eth_hashrate", [])

    @property
    async def chainId(self):
        result=await self.web3s.manager.request_blocking("eth_chainId", [])
        return int(result,base=16)



    @property
    async def gasPrice(self):
        return await self.web3s.manager.request_blocking("eth_gasPrice", [])

    @property
    async def accounts(self):
        return await self.web3s.manager.request_blocking("eth_accounts", [])


    @property
    async def blockNumber(self):
        return await self.web3s.manager.request_blocking("eth_blockNumber", [])



    async def getBalance(self, account, block_identifier=None):
        if block_identifier is None:
            block_identifier = self.defaultBlock
        return await self.web3s.manager.request_blocking(
            "eth_getBalance",
            [account, block_identifier],
        )







    async def getStorageAt(self, account, position, block_identifier=None):
        if block_identifier is None:
            block_identifier = self.defaultBlock
        return await self.web3s.manager.request_blocking(
            "eth_getStorageAt",
            [account, position, block_identifier]
        )

    async def getCode(self, account, block_identifier=None):
        if block_identifier is None:
            block_identifier = self.defaultBlock
        return await self.web3s.manager.request_blocking(
            "eth_getCode",
            [account, block_identifier],
        )

    async def getBlock(self, block_identifier, full_transactions=False):
        """
        `eth_getBlockByHash`
        `eth_getBlockByNumber`
        """
        method = select_method_for_block_identifier(
            block_identifier,
            if_predefined='eth_getBlockByNumber',
            if_hash='eth_getBlockByHash',
            if_number='eth_getBlockByNumber',
        )

        return await self.web3s.manager.request_blocking(
            method,
            [block_identifier, full_transactions],
        )

    async def getBlockTransactionCount(self, block_identifier):
        """
        `eth_getBlockTransactionCountByHash`
        `eth_getBlockTransactionCountByNumber`
        """
        method = select_method_for_block_identifier(
            block_identifier,
            if_predefined='eth_getBlockTransactionCountByNumber',
            if_hash='eth_getBlockTransactionCountByHash',
            if_number='eth_getBlockTransactionCountByNumber',
        )
        return await self.web3s.manager.request_blocking(
            method,
            [block_identifier],
        )




    async def getUncleCount(self, block_identifier):
        """
        `eth_getUncleCountByBlockHash`
        `eth_getUncleCountByBlockNumber`
        """
        method = select_method_for_block_identifier(
            block_identifier,
            if_predefined='eth_getUncleCountByBlockNumber',
            if_hash='eth_getUncleCountByBlockHash',
            if_number='eth_getUncleCountByBlockNumber',
        )
        return await self.web3s.manager.request_blocking(
            method,
            [block_identifier],
        )

    async def getUncleByBlock(self, block_identifier, uncle_index):
        """
        `eth_getUncleByBlockHashAndIndex`
        `eth_getUncleByBlockNumberAndIndex`
        """
        method = select_method_for_block_identifier(
            block_identifier,
            if_predefined='eth_getUncleByBlockNumberAndIndex',
            if_hash='eth_getUncleByBlockHashAndIndex',
            if_number='eth_getUncleByBlockNumberAndIndex',
        )
        return await self.web3s.manager.request_blocking(
            method,
            [block_identifier, uncle_index],
        )

    async def getTransaction(self, transaction_hash):
        return await self.web3s.manager.request_blocking(
            "eth_getTransactionByHash",
            [transaction_hash],
        )

    @deprecated_for("w3.eth.getTransactionByBlock")
    async def getTransactionFromBlock(self, block_identifier, transaction_index):
        """
        Alias for the method getTransactionByBlock
        Depreceated to maintain naming consistency with the json-rpc API
        """
        return await self.getTransactionByBlock(block_identifier, transaction_index)

    async def getTransactionByBlock(self, block_identifier, transaction_index):
        """
        `eth_getTransactionByBlockHashAndIndex`
        `eth_getTransactionByBlockNumberAndIndex`
        """
        method = select_method_for_block_identifier(
            block_identifier,
            if_predefined='eth_getTransactionByBlockNumberAndIndex',
            if_hash='eth_getTransactionByBlockHashAndIndex',
            if_number='eth_getTransactionByBlockNumberAndIndex',
        )
        return await self.web3s.manager.request_blocking(
            method,
            [block_identifier, transaction_index],
        )

    async def waitForTransactionReceipt(self, transaction_hash, timeout=120):
        return await wait_for_transaction_receipt(self.web3s, transaction_hash, timeout)

    async def getTransactionReceipt(self, transaction_hash):
        return await self.web3s.manager.request_blocking(
            "eth_getTransactionReceipt",
            [transaction_hash],
        )

    async def getTransactionCount(self, account, block_identifier=None):
        if block_identifier is None:
            block_identifier = self.defaultBlock
        return await self.web3s.manager.request_blocking(
            "eth_getTransactionCount",
            [
                account,
                block_identifier,
            ],
        )

    async def replaceTransaction(self, transaction_hash, new_transaction):
        current_transaction = get_required_transaction(self.web3, transaction_hash)
        return await replace_transaction(self.web3, current_transaction, new_transaction)

    async def modifyTransaction(self, transaction_hash, **transaction_params):
        assert_valid_transaction_params(transaction_params)
        current_transaction = await get_required_transaction(self.web3, transaction_hash)
        current_transaction_params = extract_valid_transaction_params(current_transaction)
        new_transaction = merge(current_transaction_params, transaction_params)
        return await replace_transaction(self.web3, current_transaction, new_transaction)

    async def sendTransaction(self, transaction):
        # TODO: move to middleware
        if 'from' not in transaction and is_checksum_address(self.defaultAccount):
            transaction = assoc(transaction, 'from', self.defaultAccount)

        # TODO: move gas estimation in middleware
        if 'gas' not in transaction:
            transaction = assoc(
                transaction,
                'gas',
                get_buffered_gas_estimate(self.web3s, transaction),
            )

        return await self.web3s.manager.request_blocking(
            "eth_sendTransaction",
            [transaction],
        )

    async def sendRawTransaction(self, raw_transaction):
        return await self.web3s.manager.request_blocking(
            "eth_sendRawTransaction",
            [raw_transaction],
        )

    async def debugTraceTransaction(self,txHash):

        return await self.web3s.manager.request_blocking(
            "debug_traceTransaction",
            [txHash],
        )

    async def sign(self, account, data=None, hexstr=None, text=None):
        message_hex = to_hex(data, hexstr=hexstr, text=text)
        return await self.web3s.manager.request_blocking(
            "eth_sign", [account, message_hex],
        )

    @async_apply_to_return_value(HexBytes)
    async def call(self, transaction, block_identifier=None):
        # TODO: move to middleware
        if 'from' not in transaction and is_checksum_address(self.defaultAccount):
            transaction = assoc(transaction, 'from', self.defaultAccount)

        # TODO: move to middleware
        if block_identifier is None:
            block_identifier = self.defaultBlock
        result=await self.web3s.manager.request_blocking(
            "eth_call",
            [transaction, block_identifier],
        )

        return result

    async def estimateGas(self, transaction):
        # TODO: move to middleware
        if 'from' not in transaction and is_checksum_address(self.defaultAccount):
            transaction = assoc(transaction, 'from', self.defaultAccount)

        return await self.web3s.manager.request_blocking(
            "eth_estimateGas",
            [transaction],
        )

    async def filter(self, filter_params=None, filter_id=None):
        if filter_id and filter_params:
            raise TypeError(
                "Ambiguous invocation: provide either a `filter_params` or a `filter_id` argument. "
                "Both were supplied."
            )
        if is_string(filter_params):
            if filter_params == "latest":
                filter_id = await self.web3s.manager.request_blocking(
                    "eth_newBlockFilter", [],
                )
                return BlockFilter(self.web3s, filter_id)
            elif filter_params == "pending":
                filter_id = await self.web3s.manager.request_blocking(
                    "eth_newPendingTransactionFilter", [],
                )
                return TransactionFilter(self.web3s, filter_id)
            else:
                raise ValueError(
                    "The filter API only accepts the values of `pending` or "
                    "`latest` for string based filters"
                )
        elif isinstance(filter_params, dict):
            _filter_id = await self.web3s.manager.request_blocking(
                "eth_newFilter",
                [filter_params],
            )
            return LogFilter(self.web3s, _filter_id)
        elif filter_id and not filter_params:
            return LogFilter(self.web3s, filter_id)
        else:
            raise TypeError("Must provide either filter_params as a string or "
                            "a valid filter object, or a filter_id as a string "
                            "or hex.")

    async def getFilterChanges(self, filter_id):
        return await self.web3s.manager.request_blocking(
            "eth_getFilterChanges", [filter_id],
        )

    async def getFilterLogs(self, filter_id):
        return await self.web3s.manager.request_blocking(
            "eth_getFilterLogs", [filter_id],
        )

    async def getLogs(self, filter_params):
        return await self.web3s.manager.request_blocking(
            "eth_getLogs", [filter_params],
        )

    async def uninstallFilter(self, filter_id):
        return await self.web3s.manager.request_blocking(
            "eth_uninstallFilter", [filter_id],
        )

    def contract(self,
                 address=None,
                 **kwargs):

        if address in self.web3s.contracts.keys():
            return self.web3s.contracts[address]

        ContractFactoryClass = kwargs.pop('ContractFactoryClass', self.defaultContractFactory)

        ContractFactory = ContractFactoryClass.factory(self.web3s, **kwargs)

        if address:
            self.web3s.contracts[address]=ContractFactory(address)
            return ContractFactory(address)
        else:
            return ContractFactory

    def setContractFactory(self, contractFactory):
        self.defaultContractFactory = contractFactory

    async def getCompilers(self):
        return await self.web3s.manager.request_blocking("eth_getCompilers", [])

    async def getWork(self):
        return await self.web3s.manager.request_blocking("eth_getWork", [])

    def generateGasPrice(self, transaction_params=None):
        if self.gasPriceStrategy:
            return self.gasPriceStrategy(self.web3s, transaction_params)

    def setGasPriceStrategy(self, gas_price_strategy):
        self.gasPriceStrategy = gas_price_strategy
