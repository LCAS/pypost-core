import unittest
import sys
import numpy as np
sys.path.append('../src/data')
from DataStructure import DataStructure
from DataAlias import DataAlias

class testDataStructure(unittest.TestCase):

    def test_len(self):
        dataStructure = DataStructure()
        self.assertEqual(len(dataStructure), 0)

        dataStructure.setDataEntry(['parameters'], [], np.ndarray((3, 4)))

        self.assertEqual(len(dataStructure), 1)

    def test_contains(self):
        dataStructure = DataStructure()
        dataStructure.setDataEntry(['parameters'], [], np.ndarray((3, 4)))
        self.assertEqual('parameters' in dataStructure, True)
        self.assertEqual('praamteres' in dataStructure, False)

    def test_setitem_broken_alias(self):
        brokenAlias = DataAlias('brokenAlias',
                                [('brokenAliasEntry', slice(0, 2))], 0)

        dataStructure = DataStructure()
        dataStructure['brokenAliasEntry'] = Exception()
        dataStructure['brokenAlias'] = brokenAlias

        self.assertRaises(ValueError, dataStructure.__setitem__,
                          'brokenAlias', np.ndarray((1, 2)))

    def test_setitem_broken_entry(self):
        dataStructure = DataStructure()
        dataStructure['brokenEntry'] = Exception()
        self.assertRaises(ValueError, dataStructure.__setitem__,
                          'brokenEntry', np.ndarray((1, 2)))

    def test_getitem_nonexisting_entry(self):
        dataStructure = DataStructure()
        self.assertRaises(ValueError, dataStructure.__getitem__,
                          'nonexisitingEntry')

    def test_getitem_broken_alias(self):
        brokenAlias = DataAlias('brokenAlias',
                                [('brokenAliasEntry', slice(0, 2))], 0)

        dataStructure = DataStructure()
        dataStructure['brokenAliasEntry'] = Exception()
        dataStructure['brokenAlias'] = brokenAlias

        self.assertRaises(ValueError, dataStructure.__getitem__,
                          'brokenAlias')

    def test_getDataEntry_empty_path(self):
        dataStructure = DataStructure()
        self.assertRaises(ValueError, dataStructure.getDataEntry, [], [])

    def test_getDataEntry_broken_path(self):
        dataStructure = DataStructure()
        self.assertRaises(ValueError, dataStructure.getDataEntry,
                          ['a', 'b'], [Exception(), ...])

    def test_setDataEntry_empty_path(self):
        dataStructure = DataStructure()
        self.assertRaises(ValueError, dataStructure.setDataEntry, [], [],
                          np.ndarray((1, 2)))

    def test_setDataEntry_invalid_data_shape(self):
        dataStructure = DataStructure()
        self.assertRaises(ValueError, dataStructure.setDataEntry, ['a'],
                          [slice(0, 5)], np.ndarray((1, 2)))

        self.assertRaises(ValueError, dataStructure.setDataEntry, ['a'],
                          [3], np.ndarray((2, 1)))

    def test_setDataEntry_invalid_indice_type(self):
        dataStructure = DataStructure()
        self.assertRaises(ValueError, dataStructure.setDataEntry, ['a'],
                          [Exception()], np.ndarray((2, 1)))



if __name__ == '__main__':
    unittest.main()
