from web3s.module import (
    Module,
)

try:
    from ethpm import (
        Package,
    )
except ImportError as exc:
    raise Exception(
        "To use the (alpha) ethpm package, you must install it explicitly. "
        "Install with `pip install --upgrade ethpm`."
    ) from exc


# Package Management is currently still in alpha
# It is not automatically available on a web3s object.
# To use the `PM` module, attach it to your web3s object
# i.e. PM.attach(web3s, 'pm')
class PM(Module):
    def get_package_from_manifest(self, manifest):
        pkg = Package(manifest)
        return pkg
