'''
# @Time    : 2020/11/1 1:06 PM
# @Author  : Jude
# @File    : setup.py
# @E-main:wangyifan7836@gmail.com
'''



from setuptools import setup, find_packages



setup(
    name = "web3s",
    version = "4.9.0",
    keywords = ("pip", "web3","ETH",'Ethereum'),
    description = "A Python library for interacting with Ethereum supporting asynchronous requests",
    long_description = "Base on the offical web3,this library supports asynchronous requests",
    license = "MIT Licence",

    url = "https://github.com/www5226448/web3s",
    author = "Jude",
    author_email = "wangyifan7836@gmail.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ['eth-abi==1.3.0',
                        'cytoolz==0.10.1',
                        'eth-hash==0.2.0',
                        'hexbytes==0.2.0',
                        'websockets==6.0',
                        'eth-account==0.3.0',
                        'requests==2.22.0',
                        'lru-dict==1.1.6',
                        'eth-utils==1.9.5',
                        'aiohttp==3.6.2',
                        ]
)


