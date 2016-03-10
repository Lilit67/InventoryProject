# 

Usage instructions
------------------------------------------------------


Run the program as:

python3 inventory_allocator.py

All command line options:

Usage: inventory_allocator.py [options]

Options:
  -h, --help            show this help message and exit
  --inventory=INVENTORY
                        Read inventory from file, default ./inv_small.txt
  --orders=ORDERS       Read orders from path, default ./test1.txt
  --random              Randomly generate orders, default False
  --streams=STREAMS     Number of streams placing orders, default 1




Examples: 

1. do not use input files, generate input

python3 inventory_allocator.py --random

2. input from several stremss

python3 inventory_allocator.py --streams 3 --random


To run the tests:

python test_inventory_allocator.py





