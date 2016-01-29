#!/bin/python
import unittest
import os

if __name__ == '__main__':
    for root, _, _ in os.walk('.'):
        if not ("__pycache__" in root or "htmlcov" in root):
            print('\n\n========== Running tests in:', root,'==========')
            suite = unittest.TestLoader().discover(root, 'test*')
            unittest.TextTestRunner().run(suite)
