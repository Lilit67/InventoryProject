#!/usr/bin/python

import sys
#import multiprocessing
import threading
#import Queue
import traceback
import json
import random
import logging
from collections import OrderedDict
from optparse import OptionParser


threadLock = threading.Lock()
logging.basicConfig(filename='debug.log', filemode='w', level=logging.DEBUG)

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
        

    def place(self, order, stream):
        '''
        1. release inventory per each product type
        2. if not available, backlog
        3 update order list
        4. halt program if no more inventory

        '''   
        with threadLock:    
            if self.checkToHalt():   
                return True
            logging.debug('Thread No: ' + str(stream))
            self.orders.append(order)
            for product in order.initial.keys():           
                remainder = self.inventory[product] - order.initial[product]

                if  remainder >= 0:
            	    self.inventory[product] = remainder
            	    order.final[product] = order.initial[product]

                else:
                    order.backlog[product] = order.backlog[product] + order.initial[product]        
               	        
     
       

    def checkToHalt(self):
            '''
            The program should stop 
            once no more inventory
            '''
        #with threadLock:
            print(self.inventory)
            values = []
            for v in self.inventory.values():
                if v == 0:
                    values.append(v)
            if values == [0,0,0,0,0]:
                
                print ('HALTING SYSTEM')
                #self.prettyPrint()
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
        verify before initialising
        
        '''
        self.header = order['Header']
        self.strm = stream
        # initialize this manually so that we do not have reference to same structure
        self.products = ['A', 'B', 'C', 'D', 'E']
        self.initial  = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
        self.final    = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
        self.backlog  = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}   

        for l in order['Lines'].keys():
           	self.initial[l] = int(order['Lines'][l])

           

    def prettyPrint(self):
        '''
        @ input
        @ output: print format, before, afger, backlog:
        1: 1,0,1,0,0::1,0,1,0,0::0,0,0,0,0
        
        '''
        
        initial = ''
        final   = ''
        backlog = ''
        for p in self.products:
            initial = initial + str(self.initial[p]) + ','
            final = final + str(self.final[p]) + ','
            backlog = backlog + str(self.backlog[p]) + ','
        
        line = str(self.header) + ': ' + str(initial) + '::' \
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
        	return order
        
        order['Header'] = ordr['Header']

        if not 'Lines' in ordr:
        	print('Malformed order description, missing entry: "Lines"')
        	return order

        for i in ordr['Lines'].keys():
            if i not in ['A','B', 'C', 'D', 'E']:
        	    print('Incorrect product name in input # ' + str(i['Header']) + ' ' + str(i))
            elif int(ordr['Lines'][i]) <=0 or int(ordr['Lines'][i]) > 5:
                print('Incorrect order value for product ' + str(i) + '  ' + str(ordr['Lines'][i]) )
            else:
            	order['Lines'][i] = int(ordr['Lines'][i])
        return order	


class Stream(threading.Thread):
    def __init__(self, TID, name, inventory):
        threading.Thread.__init__(self)
        self.threadID = TID
        self.name = name
        #self.q = q
        self.header = 1
        self.inventory = inventory


    def run(self):
        '''
        
        '''
        #threadLock.acquire()
        while True:
            order_generator = generate(self.header)
            next_line = next(order_generator)
            next_order = Order(next_line, self.name) 
            stop = self.inventory.place(next_order, self.name)
            self.header += 1  
            if stop:
                break 
        #threaLock.release()            

# Helpers
def generate(start = 1):

	order = {'Header': start, 'Lines': {} }
	for i in ['A', 'B', 'C', 'D', 'E']:
		n = random.choice(range(1,6))
		order['Lines'][i] = n

	yield order	

def getArgs():
        parser = OptionParser()
        parser.add_option('--inventory', 
                        dest = 'inventory', 
                        type = 'string',
                        help = "Enter the inventory file path",
                        default = './inv_small.txt')
        parser.add_option('--orders', 
                        dest = 'orders', 
                        type = 'string',
                        help = "Enter the orders file path",
                        default = './test1.txt')
        parser.add_option('--random', 
                        dest = 'random', 
                        action="store_true",
                        help = "Generate from random stream",
                        default = False) 
        parser.add_option('--streams', 
                        dest = 'streams', 
                        type = 'int',
                        help = "Enter the orders file path",
                        default = 1)
        (opts, args) = parser.parse_args()

        return opts, args


def main():
    '''
    Reads inventory from input file
    Reads order requests from input stream(s)
    Allocates inventory on first come first serve basis

    ''' 
    try:
 
        (opts, args) = getArgs() 
        #print (opts)
    
        # Read the initial inventory 
        with open(opts.inventory) as f:
            lines = filter(None, (line.rstrip() for line in f))
            for line in lines:
                if line.startswith('#'):    # comment
                    continue
                line = line.replace("'", "\"")
                l = json.loads(line)            # we need only first valid like
                #print (l)
                invent = Inventory(l)
                break               	

        # If random, generate the orders at random
        # System will stop when no inventory is left
        if opts.random:
            '''
            header = 1
            while True:
            #while  header < 10:      # TODO: change to True
                order_generator = generate(header)
                next_line = next(order_generator)
                stream = random.choice(range(1, opts.streams+1))
                print(next_line)
                print(stream)
                next_order = Order(next_line, stream) 
                invent.place(next_order, stream)
                header += 1
            '''

            streams = range(1, opts.streams + 1) 
            #queue = Queue.Queue(2)
            threads = []
            threadID = 1

            # Create Streams
            for number in streams:
                thread = Stream('Stream_' + str(number), number, invent)
                thread.start()
                threads.append(thread)
                threadID += 1


            for t in threads:
                t.join()          

        

        # for testing only, no multithreading intended for this case
        else:
            infofile = opts.orders
            with open(infofile) as f:

                lines = filter(None, (line.rstrip() for line in f))
                for line in lines:
                    if line.startswith('#'):    # comment
                        continue
                    line = line.replace("'", "\"")
                    l = json.loads(line)   
                    valid = Order.validate(l)
                    if valid:
                        o = Order(valid, infofile)      # TODO: validate info as well
                        invent.place(o, opts.streams)
        
        invent.prettyPrint()            

    except Exception:      # proper exception catcing and reporting
	    traceback.print_exc()
        #print(data)
        #sys.exit(-1)




if __name__ == '__main__':
    main()    

