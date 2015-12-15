import coverage
import unittest

if __name__ == '__main__':
    c = coverage.Coverage(branch=True, source=['../src/'])
    
    c.start()
    
    suite = unittest.TestLoader().discover('../tests', 'test*')
    unittest.TextTestRunner().run(suite)
   
    c.stop()
    c.report()