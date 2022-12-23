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
import subprocess


define("processes", default=4, help="Process count to start (default 4)", type=int)
define("string", help="String to find in the address", type=str)
define("start", default=False, help="search for string at the start of the address (default false)", type=bool)
define("max", default=100, help="max hit per process (default 100)", type=int)


alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
file = "./keys_upper.txt"
NETWORK_PREFIX = 60


class Key:

    def __init__(self, seed):
        key = PrivateKey.from_hex(seed)
        self.public_key = key.public_key.format(compressed=True).hex()
        self.key = key.to_hex()
        self.address = self.address()

    def identifier(self):
        return hashlib.new('ripemd160', hashlib.sha256(binascii.unhexlify(self.public_key)).digest()).digest()

    def address(self):
        vh160 = int(NETWORK_PREFIX).to_bytes(length=1, byteorder="big") + self.identifier()  # Contenu brut
        chk = hashlib.sha256(hashlib.sha256(vh160).digest()).digest()[:4]
        return base58.b58encode(vh160 + chk).decode('utf-8')


def find_it(search_for: list, start: bool):
    found = 0
    address_count = 0
    address_total = 0
    start_time = time.time()
    timer = time.perf_counter()
    with open(file, "a") as f:
        while True:
            pk = urandom(32).hex()
            key = Key(pk)
            address = key.address
            address_count += 1
            address_total += 1
            if address.isupper() == True:
                if options.start:
                    for string in search_for:
                        if address.startswith(string):
                            found += 1
                            command = ["./ravencoin-tool/bitcoin-tool", "--input-type", "private-key", "--input-format", "hex", "--public-key-compression", "compressed", "--input", pk, "--network", "ravencoin", "--output-type", "private-key-wif", "--output-format", "base58check"]
                            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            if result.returncode == 0:
                                wif = result.stdout.decode().strip()
                                print("\n" + "-" * 20)
                                print(f"\nAddress : {key.address}")
                                print(f"HEX     : {pk}")
                                print(f"WIF     : {wif}")
                                f.write("\n" + "-" * 20)
                                f.write(f"\nAddress : {key.address}")
                                f.write(f"\nHEX     : {pk}")
                                f.write(f"\nWIF     : {wif}")                        
                                if found > options.max:
                                    return
                else:
                    for string in search_for:
                        if string in address:
                            found += 1
                            command = ["./ravencoin-tool/bitcoin-tool", "--input-type", "private-key", "--input-format", "hex", "--public-key-compression", "compressed", "--input", pk, "--network", "ravencoin", "--output-type", "private-key-wif", "--output-format", "base58check"]
                            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            if result.returncode == 0:
                                wif = result.stdout.decode().strip()
                                print("\n" + "-" * 20)
                                print(f"\nAddress : {key.address}")
                                print(f"HEX     : {pk}")
                                print(f"WIF     : {wif}")
                                f.write("\n" + "-" * 20)
                                f.write(f"\nAddress : {key.address}")
                                f.write(f"\nHEX     : {pk}")
                                f.write(f"\nWIF     : {wif}")
                                if found > options.max:
                                    return
            current_time = time.time()
            if current_time - start_time > 1:
                print(f"\r{address_count * options.processes} addresses generated per second... Total: {address_total * options.processes / 1_000_000:.2f}m in {time.perf_counter() - timer:.0f} seconds", end="")
                address_count = 0
                start_time = current_time

def main():
    options.parse_command_line()
    print("Looking for UPPERCASE")
    print(f"Output in {file}")
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

if __name__ == "__main__":
    main()
