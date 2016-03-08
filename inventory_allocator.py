#!/usr/bin/python

import sys
import multiprocessing
import threading
import traceback
import json
import random
from collections import OrderedDict
from optparse import OptionParser


class Inventory(object):
    '''
    Keeps track of inventory
    Keeps track of order history
    releases inventory
    sends signal to halt system
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
        4. halt program if not more inventory

        '''        
        self.checkToHalt()

        self.orders.append(order)
        for product in order.initial.keys():
            
            remainder = self.inventory[product] - order.initial[product]
            if  remainder >= 0:
            	self.inventory[product] = remainder
            	order.final[product] = order.initial[product]

            else:
                order.backlog[product] = order.initial[product]
               	        
     
    @property
    def IDs(self):
        return len(self.orders)    
       

    def checkToHalt(self):
        '''
        The program should stop 
        once no more inventory
        '''
        if self.inventory.values() == [0,0,0,0,0]:
        	print(self.inventory)
        	print ('HALTING SYSTEM')
        	self.prettyPrint()
        	sys.exit(0)


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

        #print(order)
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
    def validate(ord):
        '''
        @input: raw order line, dict
        @ output: verified order,
        with removed invalid values, dict
        '''
        order = OrderedDict()
        order['Header'] = 0
        order['Lines'] = OrderedDict()
        if not isinstance(ord, dict):
        	return order
        
        # It is not clear if the order number should come 
        # from outside or allocated, but anyways
        order['Header'] = ord['Header']

        if not 'Lines' in ord:
        	print('Malformed order description, missing entry: "Lines"')
        	return order

        for i in ord['Lines'].keys():
            if i not in ['A','B', 'C', 'D', 'E']:
        	    #raise Exception('Incorrect product type ' + str(i))
        	    #del ord[i]
        	    print('Incorrect product name in input # ' + str(i['Header']) + ' ' + str(i))
            elif int(ord['Lines'][i]) <=0 or int(ord['Lines'][i]) > 5:
                #raise Exception('Incorrect order value for product ' + str(i) + '  ' + str(products[i]) )
                print('Incorrect order value for product ' + str(i) + '  ' + str(ord['Lines'][i]) )
            else:
            	order['Lines'][i] = int(ord['Lines'][i])
        return order	


# Helper
def generate(start = 1):

	order = {'Header': start, 'Lines': {} }
	for i in ['A', 'B', 'C', 'D', 'E']:
		n = random.choice(range(1,6))
		order['Lines'][i] = n

	yield order	

def main():
    '''
    Reads inventory from input file
    Reads order requests from input stream(s)
    Allocates inventory on first come first serve basis

    '''
    #inventory1 = {'A': 150, 'B': 150, 'C': 100, 'D': 100, 'E': 200}
    #inventory2 = {'A': 2, 'B': 3, 'C': 1, 'D': 0, 'E': 0}
 
    try:
        # lets do it from file
        #infofile = './test1.txt'

        #invent = Inventory(inventory1)

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

        print (opts)
    
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

            header = 1
            #print "RANDOM"
            while  header < 10:      # TODO: change to True
                order_generator = generate(header)
                next_line = next(order_generator)
                stream = random.choice(range(1, opts.streams+1))
                print(next_line)
                print(stream)
                next_order = Order(next_line, stream) 
                invent.place(next_order, stream)
                header += 1


        

        
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
                        invent.place(o)
        
        invent.prettyPrint()            

    except Exception:      # proper exception catcing and reporting
	    traceback.print_exc()
        #print(data)
        #sys.exit(-1)




if __name__ == '__main__':
    main()    

