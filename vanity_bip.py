"""
Test - Generate vanity ecdsa address for Raptoreum, mine for BIP32 mnemonics

Affero GPL
You can use and modify freely, including in paid services and saas,
as long as you release the source code and modifications.
"""


from os import urandom
import hashlib
# from secrets import token_hex
from multiprocessing import Process
from coincurve import PrivateKey
import base58
from bip_utils import Bip39SeedGenerator, Bip32, Bip39MnemonicGenerator

# TODO: click would be a better choice than tornado. I'm lazy.
from tornado.options import define, options


define("processes", default=4, help="Process count to start (default 4)", type=int)
define("string", help="String to find in the address", type=str)
define("case", default=False, help="be case sensitive (default false)", type=bool)
define("max", default=100, help="max hit per process (default 100)", type=int)

define("indices", default=2, help="Number of HD addresses per mnemonic to test (default 2)", type=int)


alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


class Key:

    def __init__(self, seed):
        key = PrivateKey.from_hex(seed)
        self.public_key = key.public_key.format(compressed=True).hex()
        self.key = key.to_hex()  # == seed
        self.address = self.address()

    def identifier(self):
        """Returns double hash of pubkey as per btc standards"""
        return hashlib.new('ripemd160', hashlib.sha256(bytes.fromhex(self.public_key)).digest()).digest()

    def address(self):
        """Returns properly serialized address from pubkey as per btc standards"""
        vh160 = int(60).to_bytes(length=1, byteorder="big") + self.identifier()  # raw content
        chk = hashlib.sha256(hashlib.sha256(vh160).digest()).digest()[:4]
        return base58.b58encode(vh160 + chk).decode('utf-8')


def get_addresses_from(mnemonic):
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    addresses = []
    # TODO: manually derive last index from one parent to save some time, allow other derive paths
    for i in range(0, options.indices - 1):
        bip32_ctx = Bip32.FromSeedAndPath(seed_bytes, f"m/0'/2'/{i}")
        key = Key(bip32_ctx.PrivateKey().Raw().ToHex())
        addresses.append(key.address)
    return addresses


def find_it(search_for: list):
    found = 0
    while True:
        entropy = urandom(32)
        mnemonic = Bip39MnemonicGenerator().FromEntropy(entropy)
        # pk = token_hex(32)  # +50% time, but supposed to be cryptographically secure
        addresses = get_addresses_from(mnemonic)
        for string in search_for:
            for index, address in enumerate(addresses):
                if not options.case:
                    address = address.lower()
                if string in address:
                    print(address, index, mnemonic)
                    found += 1
                    if found > options.max:
                        return


if __name__ == "__main__":
    options.parse_command_line()

    print("Looking for '{}'".format(options.string))
    if not options.case:
        options.string = options.string.lower()
        print("Case InsEnsITivE")
    else:
        print("Case sensitive")
    print(f"{options.indices} tests per mnemonic")
    print("m/0'/2'/i derive path")
    # Check charset is ok ? not easy with case insensitive...

    processes = []
    if "|" in options.string:
        search_for = options.string.split("|")
    else:
        search_for = [options.string]
    for i in range(options.processes):
        p = Process(target=find_it, args=(search_for, ))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

