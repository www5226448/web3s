def construct_user_agent(class_name):
    #from web3s import __version__ as web3_version
    web3_version='4.8.0'

    user_agent = 'Web3.py/{version}/{class_name}'.format(
        version=web3_version,
        class_name=class_name,
    )
    return user_agent
