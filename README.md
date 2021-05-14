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
- `--case=false` or `--case=true` case sensitive search? (way longer, false by default)
- `--max=100` max number of hits per process.

The script spits out addresses and related privatekey (raw hex form), one per line.

## Licence

Affero GPL  
You can use and modify freely, including in paid services and saas, as long as you release the source code and modifications.

# Donation Address

`RAoKaVD9D2jGXuRUEsJmLXYztr3Kdnqsyf` 