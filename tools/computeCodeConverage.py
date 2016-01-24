'''
This tool requires coverage.py to be installed. See
https://coverage.readthedocs.org/en/coverage-4.0.3/install.html
for more information.
'''

import coverage
import unittest

if __name__ == '__main__':
    c = coverage.Coverage(branch=True, source=['../src/'], omit=['*Interface*', '*__init__.py'])

    c.start()

    suite = unittest.TestLoader().discover('../tests', 'test*')
    unittest.TextTestRunner().run(suite)

    c.stop()
    c.report()
    c.html_report()
