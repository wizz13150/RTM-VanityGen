"""
Test - Generate vanity ecdsa address for Raptoreum

Affero GPL
You can use and modify freely, including in paid services and saas,
as long as you release the source code and modifications.
"""



from os import urandom
from time import time
import hashlib
import time
import binascii
from concurrent.futures import ProcessPoolExecutor
from coincurve import PrivateKey
import base58
from tornado.options import define, options

define("processes", default=4, help="Process count to start (default 4)", type=int)
define("string", help="String to find in the address", type=str)
define("start", default=False, help="search for string at the start of the address (default false)", type=bool)
define("case", default=False, help="be case sensitive (default false)", type=bool)
define("max", default=100, help="max hit per process (default 100)", type=int)


alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


class Key:

    def __init__(self, seed):
        key = PrivateKey.from_hex(seed)
        self.public_key = key.public_key.format(compressed=True).hex()
        self.key = key.to_hex()
        self.address = self.address()

    def identifier(self):
        """Renvoie le double hash de la clé publique selon les standards de BTC"""
        return hashlib.new('ripemd160', hashlib.sha256(binascii.unhexlify(self.public_key)).digest()).digest()

    def address(self):
        """Renvoie l'adresse sérialisée correctement à partir de la clé publique selon les standards de BTC"""
        vh160 = int(60).to_bytes(length=1, byteorder="big") + self.identifier()  # Contenu brut
        chk = hashlib.sha256(hashlib.sha256(vh160).digest()).digest()[:4]
        return base58.b58encode(vh160 + chk).decode('utf-8')


def find_it(search_for: list, start: bool):
    found = 0
    address_count = 0
    start_time = time.time()
    for char in options.string:
        if options.case:
            if char not in alphabet and char != "|":
                invalid_chars.append(char)
        else:
            if char.lower() not in alphabet.lower() and char != "|":
                invalid_chars.append(char)
    if invalid_chars:
        print(f"Characters '{', '.join(invalid_chars)}' not allowed, try again :'( See : '{alphabet}'.")
        return
    while True:
        pk = urandom(32).hex()
        key = Key(pk)
        address = key.address
        address_count += 1
        if not options.case:
            address = address.lower()
        if start:
            if address.startswith(options.string):
                print("\n" + "-" * 20)
                print(f"\nAddress : {key.address}")
                print(f"HEX     : {pk}")
                found += 1
                if found > options.max:
                    return
        else:
            for string in search_for:
                if string in address:
                    print("\n" + "-" * 20)
                    print(f"\nAddress : {key.address}")
                    print(f"HEX     : {pk}")
                    found += 1
                    if found > options.max:
                        return
        current_time = time.time()
        if current_time - start_time > 1:
            print(f"\r{address_count * options.processes} addresses generated per second... ", end="")
            address_count = 0
            start_time = current_time

if __name__ == "__main__":
    options.parse_command_line()

    print("Looking for '{}'".format(options.string))
    if not options.case:
        options.string = options.string.lower()
        print("Case InsEnsITivE")
    else:
        print("Case sensitive")
        
    print(f"{options.processes} threads used")
    if options.start:
        print("Search at beginning of address")
    else:
        print("Search anywhere in the address")
        
    processes = []
    if "|" in options.string:
        search_for = options.string.split("|")
    else:
        search_for = [options.string]
    with ProcessPoolExecutor(max_workers=options.processes) as executor:
        for i in range(options.processes):
            executor.submit(find_it, search_for, options.start)

    for p in processes:
        p.join()
