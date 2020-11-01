class Module:
    web3s = None


    def __init__(self, web3s):
        self.web3s = web3s


    @classmethod
    def attach(cls, target, module_name=None):
        if not module_name:
            module_name = cls.__name__.lower()

        if hasattr(target, module_name):
            raise AttributeError(
                "Cannot set {0} module named '{1}'.  The web3s object "
                "already has an attribute with that name".format(
                    target,
                    module_name,
                )
            )

        if isinstance(target, Module):
            web3s = target.web3s
        else:
            web3s = target

        setattr(target, module_name, cls(web3s))
