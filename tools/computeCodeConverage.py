import coverage
import unittest

if __name__ == '__main__':
    c = coverage.Coverage(branch=True, source=['../src/'], omit=['*Interface*', '*__init__.py'])
    
    c.start()
    
    suite = unittest.TestLoader().discover('../tests', 'test*')
    unittest.TextTestRunner().run(suite)
   
    c.stop()
    c.report()