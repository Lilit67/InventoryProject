import unittest
import os
import subprocess
import inspect



class InventoryAllocation(unittest.TestCase):
    
    
    def test_1(self):
        strm = './test1.ixt'
        inv = './inv_small.txt'
 
        golden = './test1.txt: 1: 1,0,1,0,0::1,0,1,0,0::0,0,0,0,0\n.'+ \
        '/test1.txt: 2: 0,0,0,0,5::0,0,0,0,0::0,0,0,0,5\n.'+\
        '/test1.txt: 3: 0,0,0,4,0::0,0,0,0,0::0,0,0,4,0\n.'+\
        '/test1.txt: 4: 1,0,1,0,0::1,0,0,0,0::0,0,1,0,0\n.'+\
        '/test1.txt: 5: 0,3,0,0,0::0,3,0,0,0::0,0,0,0,0\n'
        out = subprocess.check_output(['python', 'inventory_allocator.py', \
            '--orders', './test1.txt'], \
            stdin=None, stderr=None, shell=False, universal_newlines=False)
        # python3 returns byte string
        out = out.decode('utf-8')
        self.assertOutput(golden, out, inspect.stack()[0][3])


    def test_wrong_input(self):
        '''
        Tests invalid order rejection
        '''
        strm = './test2.txt'
        inv = './inv_small.txt'
 
        golden = './test2.txt: 1: 4,2,2,0,0::0,2,0,0,0::4,0,2,0,0\n' + \
                 './test2.txt: 2: 0,0,0,4,2::0,0,0,0,0::0,0,0,4,2\n' +\
                './test2.txt: 3: 4,3,2,0,0::0,0,0,0,0::4,3,2,0,0\n' 
        out = subprocess.check_output(['python', 'inventory_allocator.py', \
            '--orders', './test2.txt', '-g'], \
            stdin=None, stderr=None, shell=False, universal_newlines=False)
        # python3 returns byte string
        out = out.decode('utf-8')
        self.assertOutput(golden, out, inspect.stack()[0][3])    


    def test_python2To3(self):
        ret = os.system('python inventory_allocator.py')
        self.assertEqual(ret, 0)
        ret = os.system('python3 inventory_allocator.py')
        self.assertEqual(ret, 0)

    def test_random_option(self):    
        ret = os.system('python inventory_allocator.py --streams 2')
        self.assertEqual(ret, 0)
        ret = os.system('python3 inventory_allocator.py --streams 3')
        self.assertEqual(ret, 0)

    def test_random_streams(self):    
        ret = os.system('python3 inventory_allocator.py --streams 4 --inventory inv_med.txt')
        self.assertEqual(ret, 0)

    def assertOutput(self, golden, output, testname):
        g_lines = str(golden).strip('b').split('\\n')        
        o_lines = output.strip('b').split('\\n')

        for g, o in zip(g_lines, o_lines):

            message = 'Golden vs. Output difference in test: %s differ: %s AND %s ' % \
                 (testname, g, o)
            self.assertEqual(g, o, message)



if __name__ == '__main__':
    unittest.main()




