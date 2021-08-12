# web3s

This is a Python library for interacting with Ethereum supporting asynchronous requests.

If you want to synchronize a method, you can use the sync method in utils to change the asynchronous method to synchronous.

You can use pip to install:
```shell
$ pip install web3s
```

All APIs are consistent with the web3py 4.8.0 version.
This package only suppoorts the web3 http provider.

Please note that some provider may doesn't support the txpool api.



This package is compatible with EIP-1559,EIP-2718 and EIP-2939.

check eth_accounts newest release how to sign a EIP1559 tx. 
https://github.com/ethereum/eth-account/pull/117/files#diff-05c5ec1ce64e45128808675b9e1538658cb67e18148cbc9a7d0b20a4c0cf8f2dR685


