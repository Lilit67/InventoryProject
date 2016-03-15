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
  --orders=ORDERS       Read orders from path, default
  --streams=STREAMS     Number of streams placing orders, default 1
  -g, --debug           Output debug into debug.log, default False



Examples: 

1. Read data from input file, runs for one stream only

python3 inventory_allocator.py --orders ./test1.txt

2. input from several streams, input data generated randomly

python3 inventory_allocator.py --streams 3


To run the tests:

python test_inventory_allocator.py





