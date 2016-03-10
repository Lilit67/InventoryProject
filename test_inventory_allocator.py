import unittest
import os
import subprocess



class InventoryAllocation(unittest.TestCase):
    
    
    def test_1(self):
        strm = './test1.ixt'
        inv = './inv_small.txt'
        '''
        golden = '/test1.txt: 1: 1,0,1,0,0,::1,0,1,0,0,::0,0,0,0,0,\n' + \
           './test1.txt: 2: 0,0,0,0,5,::0,0,0,0,0,::0,0,0,0,5,\n' + \
                './test1.txt: 3: 0,0,0,4,0,::0,0,0,0,0,::0,0,0,4,0,\n' + \
                './test1.txt: 4: 1,0,1,0,0,::1,0,0,0,0,::0,0,1,0,0,\n' + \
                './test1.txt: 5: 0,3,0,0,0,::0,3,0,0,0,::0,0,0,0,0,\n'
        '''        
        golden = b'./test1.txt: 1: 1,0,1,0,0,::1,0,1,0,0,::0,0,0,0,0,\n./test1.txt: 2: 0,0,0,0,5,::0,0,0,0,0,::0,0,0,0,5,\n./test1.txt: 3: 0,0,0,4,0,::0,0,0,0,0,::0,0,0,4,0,\n./test1.txt: 4: 1,0,1,0,0,::1,0,0,0,0,::0,0,1,0,0,\n./test1.txt: 5: 0,3,0,0,0,::0,3,0,0,0,::0,0,0,0,0,\n'
        out = subprocess.check_output(['python', 'inventory_allocator.py', '--orders', './test1.txt'], \
              stdin=None, stderr=None, shell=False, universal_newlines=False)
        self.assertEqual(golden, out)


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
        ret = os.system('python3 inventory_allocator.py --streams 4 --inventory inv_large.txt')
        self.assertEqual(ret, 0)


if __name__ == '__main__':
    unittest.main()




