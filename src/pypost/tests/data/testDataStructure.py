import unittest
import numpy as np
from pypost.data.DataStructure import DataStructure
from pypost.data.DataAlias import DataAlias
from pypost.data.DataEntry import DataEntry


class testDataStructure(unittest.TestCase):

    def test_createEntry_twice(self):
        dataStructure = DataStructure(5)

        dataEntry = DataEntry('parameters', 3)
        dataStructure.createEntry('parameters', dataEntry)

        self.assertRaises(ValueError, dataStructure.createEntry, 'parameters', dataEntry)

    def test_len(self):
        dataStructure = DataStructure(5)
        self.assertEqual(len(dataStructure), 0)
        
        dataEntry = DataEntry('parameters', 3)
        dataStructure.createEntry('parameters', dataEntry)

        self.assertEqual(len(dataStructure), 1)

    def test_contains(self):
        dataStructure = DataStructure(5)
        dataEntry = DataEntry('parameters', 3)
        dataStructure.createEntry('parameters', dataEntry)
        self.assertEqual('parameters' in dataStructure, True)
        self.assertEqual('praamteres' in dataStructure, False)

    def test_setitem_non_existing_entry(self):
        dataStructure = DataStructure(5)
        self.assertRaises(KeyError, dataStructure.__setitem__,
                          'noEntry', np.ndarray((1, 2)))

    def test_setitem_non_ndarray(self):
        dataStructure = DataStructure(5)
        dataEntry = DataEntry('parameters', 3)
        dataStructure.createEntry('parameters', dataEntry)

        self.assertRaises(ValueError, dataStructure.__setitem__,
                          'parameters', None)

    def test_setitem_invalid_shape(self):
        dataStructure = DataStructure(5)
        dataStructure.createEntry('parameters', DataEntry('parameters', 3))
        self.assertRaises(ValueError, dataStructure.__setitem__,
                          'parameters', np.ndarray((1, 2)))


    def test_getitem_nonexisting_entry(self):
        dataStructure = DataStructure(5)
        self.assertRaises(ValueError, dataStructure.__getitem__,
                          'nonexisitingEntry')

    def test_getitem_broken_alias(self):
        brokenAlias = DataAlias('brokenAlias',
                                [('brokenAliasEntry', slice(0, 2))], 0)

        dataStructure = DataStructure(5)
        dataStructure.createAlias('brokenAliasEntry', Exception())
        dataStructure.createAlias('brokenAlias', brokenAlias)

        self.assertRaises(ValueError, dataStructure.__getitem__,
                          'brokenAlias')

    def test_getDataEntry_empty_path(self):
        dataStructure = DataStructure(5)
        self.assertRaises(ValueError, dataStructure.getDataEntry, [], [])

    def test_getDataEntry_broken_path(self):
        dataStructure = DataStructure(5)
        self.assertRaises(ValueError, dataStructure.getDataEntry,
                          ['a', 'b'], [Exception(), ...])

    def test_getDataEntry_invalid_indices_type(self):
        dataStructure = DataStructure(5)
        dataStructure.createEntry('parameters', DataEntry('parameters',3))

        self.assertRaises(ValueError, dataStructure.getDataEntry,
            ['parameters'], 'x')

    def test_setDataEntry_empty_path(self):
        dataStructure = DataStructure(5)
        self.assertRaises(ValueError, dataStructure.setDataEntry, [], [],
                          np.ndarray((1, 2)))

    def test_setDataEntry_invalid_data_shape(self):
        dataStructure = DataStructure(5)
        self.assertRaises(ValueError, dataStructure.setDataEntry, ['a'],
                          [slice(0, 5)], np.ndarray((1, 2)))

        self.assertRaises(ValueError, dataStructure.setDataEntry, ['a'],
                          [3], np.ndarray((2, 1)))

    def test_setDataEntry_invalid_indice_type(self):
        dataStructure = DataStructure(5)
        self.assertRaises(ValueError, dataStructure.setDataEntry, ['a'],
                          [Exception()], np.ndarray((2, 1)))



if __name__ == '__main__':
    unittest.main()
