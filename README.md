Wizz's Changes:
- Parameter --start to search for string at the start of the address.
- Show number of addresses generated per sec, for all threads. (~320K/sec for a Rysen 3900x with 24 threads)
- Check if every pattern's characters are allowed or not. Print what's wrong.
- Imported Ravencoin-Tool, using it to convert results to WIF.
- Write results in a text file, in the current directory. Set line 30.

Example :

![image](https://user-images.githubusercontent.com/22177081/209399927-4ab49fb2-2c8a-43b6-a876-6dcc146e47ae.png)


- Search Uppercase only:
    
    Run `python3 vanity_upper.py --processes="xx"`

Example :

![image](https://user-images.githubusercontent.com/22177081/209406755-91d9021e-9a88-49b6-af22-5b858be12470.png)



__________________________________________________________________________________________________________

__________________________________________________________________________________________________________

__________________________________________________________________________________________________________

__________________________________________________________________________________________________________



# rtm-vanity
A vanity address generator for Raptoreum - RTM

## Install

`pip3 install -r requirements.txt`

## Usage

Simple run with default params, string is the thing to search for.   
The longer the string the longer the search.  

`python3 vanity.py --string="Egg"`


Command line options:  
- `--processes=4` number of processes to use, default 4
- `--start` search for string at the start of the address (default false)"
- `--case=false` or `--case=true` case sensitive search? (way longer, false by default)
- `--max=100` max number of hits per process.

The script spits out addresses and related privatekey (raw hex form), one per line.

## Search for multiple matches

Encode the various strings to search for with | as separator.  
Ex:   
`python3 vanity.py --string="Egg|3gg"` will search for both "Egg" and "3gg". Add as many as you need.

## Mine for BIP32 mnemonics

Way less optimized, slower and less efficient by nature (half entropy).  
Uses Stacy bot derive path.

Ex:  
`python3 vanity_bip.py --string="rapt" --indices=5`

Command line options:  
- same as vanity.py, plus:  
- `--indices=2` number of indices to test per mnemonic, default 2 (Stacy bot uses 2 first indices)

# Warnings

If you require case sensitive matching, search will be way longer, and some strings you just can't have.  
For instance you can have a L but no l. You can Have o (the letter, lowercap) but no O (upper case) and no 0 (the number).  

Full charset is `123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz`  
This is part of base58 encoding, no way around that.

## Licence

Affero GPL  
You can use and modify freely, including in paid services and saas, as long as you release the source code and modifications.

# Donation Address

`RAoKaVD9D2jGXuRUEsJmLXYztr3Kdnqsyf` 
