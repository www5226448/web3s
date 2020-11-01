import asyncio

import web3s

w3 = web3s.Web3s(web3s.Web3s.HTTPProvider('https://the-holy-mountain.quiknode.io/8abb50e2-d509-40e5-aa8a-32a62cec92da/CVfNB7IyMQfIH1IqEsTfAJRA6bgFJpIM4y7YlqTiz89dFsMHTpASxKVA1kr58e6-HDfZRZ8J6O9dXTMeVCTOhg==/'))





contrats = w3.eth.contract('0xdAC17F958D2ee523a2206206994597C13D831ec7', abi=open('ERC20.txt').read())

call_contract = contrats.functions.balanceOf('0x5576FBC0910Cf6Ea812A63cE4E21Dc3Ee26F78B2').call()



test_item = [w3.isConnected(),
             w3.eth.blockNumber,
             w3.eth.getBalance('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'),

             w3.eth.getStorageAt('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 0),
             w3.eth.getBlock(11117310),
             w3.eth.getBlockTransactionCount(11117310),
             w3.eth.getUncleByBlock(11117310, 0),
             w3.eth.getTransaction('0x39b416cdb762481a8a4ad70afaef10b52e59efcf52d13063a6554962a8c22e9f'),
             w3.eth.getTransactionByBlock(11117310, 0),
             w3.eth.waitForTransactionReceipt('0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060'),
             w3.eth.getTransactionReceipt('0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060'),
             # not yet mined
             w3.eth.getTransactionCount('0x39d9096Acb38D2E84409F6A384e662dcA3ba86Ee'),
             w3.eth.gasPrice,
             w3.eth.chainId,
             w3.txpool.content,

             call_contract
             ]



async def main():
    await asyncio.gather(*test_item)


async def get_new_transfer(address):
    filter = await w3.eth.filter('pending')

    while True:

        new_events=await filter.get_new_entries()
        print(new_events)
        await asyncio.sleep(2)








loop=asyncio.get_event_loop()
#r=loop.run_until_complete(get_new_transfer('0xdAC17F958D2ee523a2206206994597C13D831ec7'))

from web3s.utils import sync
r=sync(w3.isConnected())
print(r)



