#!/usr/bin/python

import sys
import threading
import traceback
import json
import random
import logging
from collections import OrderedDict
from optparse import OptionParser



threadLock = threading.Lock()
logging.basicConfig(filename='debug.log', filemode='w', level=logging.DEBUG)
Products = ['A', 'B', 'C', 'D', 'E']

class Inventory(object):
    '''
    Keeps track of inventory
    Keeps track of order history
    releases inventory
    halts system
    prints out order history
    '''
    
    def __init__(self, inventory):
        '''
        set up initial inventory
        initialize data structures
        '''
        self.inventory = inventory    
        self.orders = []
        self.counter = 0
        

    def place(self, order, streamID):
        '''
        1. release inventory per each product type
        2. if not available, backlog
        3 update order list
        4. halt program if no more inventory

        '''   
        with threadLock:    
            if self.checkToHalt():   
                return True
            logging.debug('Thread No: ' + str(streamID))
            logging.debug("Inventory AFTER release of order #" + \
                str(order.header) + ' ' + str(self.inventory))
            logging.debug("Requested " + str(order.initial))

            self.orders.append(order)
            for product in order.initial.keys():           
                remainder = self.inventory[product] - order.initial[product]

                if  remainder >= 0:
            	    self.inventory[product] = remainder
            	    order.final[product] = order.initial[product]

                else:
                    order.backlog[product] = order.backlog[product] + \
                    order.initial[product] 

            logging.debug("Inventory AFTER release of order #" + \
                str(order.header) + ' ' + str(self.inventory))   	        
           

    def checkToHalt(self):
            '''
            The program should stop 
            once no more inventory
            '''  
            values = []
            for v in self.inventory.values():
                if v == 0:
                    values.append(v)
            if values == [0,0,0,0,0]:
                
                logging.debug('HALTING SYSTEM')

                return True
            return False    


    def prettyPrint(self):
        '''
        Print order history
        '''       
        for order in self.orders:            
            order.prettyPrint()    



class Order(object):
        
    def __init__(self, order, stream):
        '''
        Construct order line
        '''
        self.header = order['Header']
        self.strm = stream
    
        self.products = Products
        self.initial  = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
        self.final    = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
        self.backlog  = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}   

        for l in order['Lines'].keys():
           	self.initial[l] = int(order['Lines'][l])
          

    def prettyPrint(self):
        '''
        @ input
        @ output: print format- before, after, backlog:
        1: 1,0,1,0,0::1,0,1,0,0::0,0,0,0,0
        
        '''   
        initial = ''
        final   = ''
        backlog = ''
        for p in self.products:
            initial = initial + str(self.initial[p]) + ','
            final = final + str(self.final[p]) + ','
            backlog = backlog + str(self.backlog[p]) + ','

        line = str(self.strm) + ': ' + str(self.header) + ': ' + str(initial) + '::' \
            + str(final) + '::' + str(backlog)
        
        print(line)   

    	
    @staticmethod
    def validate(ordr):
        '''
        @input: raw order line, dict
        @ output: verified order,
        with removed invalid values, dict
        '''
        order = OrderedDict()
        order['Header'] = 0
        order['Lines'] = OrderedDict()
        if not isinstance(ordr, dict):
        	return None
        
        order['Header'] = ordr['Header']

        if not 'Lines' in ordr:
        	logging.debug('Malformed order description, missing entry: "Lines"')
        	return None

        for i in ordr['Lines'].keys():
            if i not in ['A','B', 'C', 'D', 'E']:
        	    logging.debug('Incorrect product name in input # ' + \
                    str(i['Header']) + ' ' + str(i))
            elif int(ordr['Lines'][i]) <=0 or int(ordr['Lines'][i]) > 5:
                logging.debug('Incorrect order value for product ' + str(i) + \
                    '  ' + str(ordr['Lines'][i]) )
            else:
            	order['Lines'][i] = int(ordr['Lines'][i])
        return order	


class Stream(threading.Thread):
    def __init__(self, TID, name, inventory):
        threading.Thread.__init__(self)
        self.threadID = TID
        self.name = name
        self.header = 1
        self.inventory = inventory


    def run(self):
        '''
        place orders
        from one stream
        '''
        while True:
            order_generator = generate(self.header)
            next_line = next(order_generator)
            next_order = Order(next_line, self.threadID) 
            stop = self.inventory.place(next_order, self.threadID)
            self.header += 1  
            if stop:
                break 
           

# Helpers
def generate(start = 1):
    '''
    Generate random order line
    '''
    order = {'Header': start, 'Lines': {} }
    for i in ['A', 'B', 'C', 'D', 'E']:
	    n = random.choice(range(1,6))
	    order['Lines'][i] = n

    yield order	


def getArgs():
        '''
        Parse command line
        '''
        parser = OptionParser()
        parser.add_option('--inventory', 
                        dest = 'inventory', 
                        type = 'string',
                        help = "Read inventory from file, default %default",
                        default = './inv_small.txt')
        parser.add_option('--orders', 
                        dest = 'orders', 
                        type = 'string',
                        help = "Read orders from path, default %default",
                        default = '')
        parser.add_option('--streams', 
                        dest = 'streams', 
                        type = 'int',
                        help = "Number of streams placing orders, default %default",
                        default = 1)
        (opts, args) = parser.parse_args()

        logging.debug('Command-line arguments: ' + str(opts))
        return opts, args


def getInventory(filepath):
    '''
    Read the file for the initial 
    inventory values.
    For testsing with different files

    ''' 
    with open(filepath) as f:
        lines = filter(None, (line.rstrip() for line in f))
        for line in lines:
            if line.startswith('#'):    # comment
                continue
            line = line.replace("'", "\"")
            l = json.loads(line) 
            break 
    return l 


def getOrdersFromFile(filepath):
    stream = []
    with open(filepath) as f:

        lines = filter(None, (line.rstrip() for line in f))
        for line in lines:
            if line.startswith('#'): 
                continue
            line = line.replace("'", "\"")
            l = json.loads(line)   
            valid = Order.validate(l)  
            if valid:
                stream.append(valid)

    return stream                                              



def main():
    '''
    Reads inventory from input file
    Reads order requests from input stream(s)
    Allocates inventory on first come first serve basis

    ''' 
    try:
 
        (opts, args) = getArgs() 
        invent = Inventory(getInventory(opts.inventory))

        # this option is only for testing purposes
        # having hard coded input 
        # seems easier to track. 
        if len(opts.orders):
            streams = 1
            random = False
            infofile = opts.orders
            with open(infofile) as f:

                lines = filter(None, (line.rstrip() for line in f))
                for line in lines:
                    if line.startswith('#'): 
                        continue
                    line = line.replace("'", "\"")
                    l = json.loads(line)   
                    valid = Order.validate(l)
                    if valid:
                        o = Order(valid, infofile)  
                        invent.place(o, infofile)

        
        # Multistream option works only with
        # random stream generations
        # the idea is to have each stream
        # to generate its own orders at
        # any time moment, which will be hard
        # to satisfy with ready made file input
        # no much sense to have 10 files if we want 10 streams 
        # System will stop when no inventory is left 

        else:    
            
            streams = range(1, opts.streams + 1) 
            threads = []

            # Create Streams
            for number in streams:
                thread = Stream('Stream_' + str(number), number, invent)
                thread.start()
                threads.append(thread)

            for t in threads:
                t.join()                 


        
        invent.prettyPrint()            

    except Exception:
        traceback.print_exc()
        sys.exit(-1)


if __name__ == '__main__':
    main()    

