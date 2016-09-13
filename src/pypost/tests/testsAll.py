#!/bin/python
import unittest, os

if __name__ == '__main__':
    for root, _, _ in os.walk(os.path.dirname(os.path.realpath(__file__))):
        if not ("__pycache__" in root or "htmlcov" in root):
            print('\n\n========== Running tests in:', root,'==========')
            suite = unittest.TestLoader().discover(root, 'test*')
            unittest.TextTestRunner().run(suite)
