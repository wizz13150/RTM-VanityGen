"""
Test - Generate vanity ecdsa address for Raptoreum

Affero GPL
You can use and modify freely, including in paid services and saas,
as long as you release the source code and modifications.
"""


from os import urandom
from time import time
import hashlib
# from secrets import token_hex
from multiprocessing import Process
from coincurve import PrivateKey
import base58

# TODO: click would be a better choice than tornado. I'm lazy.
from tornado.options import define, options


define("processes", default=4, help="Process count to start (default 4)", type=int)
define("string", help="String to find in the address", type=str)
define("case", default=False, help="be case sensitive (default false)", type=bool)
define("max", default=100, help="max hit per process (default 100)", type=int)

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


def find_it(string: str):
    found = 0
    while True:
        pk = urandom(32).hex()
        # pk = token_hex(32)  # +50% time, but supposed to be cryptographically secure
        key = Key(pk)
        address = key.address
        if not options.case:
            address = address.lower()
        if string in address:
            print(key.address, pk)
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
    # Check charset is ok ? not easy with case insensitive...

    processes = []
    for i in range(options.processes):
        p = Process(target=find_it, args=(options.string,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    """
    start = time()
    for i in range(100000):
        pk = urandom(32).hex()
        key = Key(pk)
    print(time() - start)
    """
