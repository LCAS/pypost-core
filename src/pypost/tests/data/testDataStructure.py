import unittest
import numpy as np
from pypost.data import DataStructure, DataAlias, DataEntry, DataManager


class testDataStructure(unittest.TestCase):
    
    def setUp(self):
        self.dataManager = DataManager('episodes')

    def test_createEntry_twice(self):
        dataStructure = DataStructure(self.dataManager, 5)

        dataEntry = DataEntry('parameters', 3)
        dataStructure.createEntry('parameters', dataEntry)

        self.assertRaises(ValueError, dataStructure.createEntry, 'parameters', dataEntry)

    def test_len(self):
        dataStructure = DataStructure(self.dataManager, 5)
        self.assertEqual(len(dataStructure), 0)
        
        dataEntry = DataEntry('parameters', 3)
        dataStructure.createEntry('parameters', dataEntry)

        self.assertEqual(len(dataStructure), 1)

    def test_contains(self):
        dataStructure = DataStructure(self.dataManager, 5)
        dataEntry = DataEntry('parameters', 3)
        dataStructure.createEntry('parameters', dataEntry)
        self.assertEqual('parameters' in dataStructure, True)
        self.assertEqual('praamteres' in dataStructure, False)

    def test_setitem_non_existing_entry(self):
        dataStructure = DataStructure(self.dataManager, 5)
        self.assertRaises(KeyError, dataStructure.__setitem__,
                          'noEntry', np.ndarray((1, 2)))

    def test_setitem_non_ndarray(self):
        dataStructure = DataStructure(self.dataManager, 5)
        dataEntry = DataEntry('parameters', 3)
        dataStructure.createEntry('parameters', dataEntry)

        self.assertRaises(ValueError, dataStructure.__setitem__,
                          'parameters', None)

    def test_setitem_invalid_shape(self):
        dataStructure = DataStructure(self.dataManager, 5)
        dataStructure.createEntry('parameters', DataEntry('parameters', 3))
        self.assertRaises(ValueError, dataStructure.__setitem__,
                          'parameters', np.ndarray((1, 2)))


    def test_getitem_nonexisting_entry(self):
        dataStructure = DataStructure(self.dataManager, 5)
        self.assertRaises(ValueError, dataStructure.__getitem__,
                          'nonexisitingEntry')

    def test_getitem_broken_alias(self):
        brokenAlias = DataAlias('brokenAlias',
                                [('brokenAliasEntry', slice(0, 2))], 0)

        dataStructure = DataStructure(self.dataManager, 5)
        dataStructure.createAlias('brokenAliasEntry', Exception())
        dataStructure.createAlias('brokenAlias', brokenAlias)

        self.assertRaises(ValueError, dataStructure.__getitem__,
                          'brokenAlias')

    def test_getDataEntry_empty_path(self):
        dataStructure = DataStructure(self.dataManager, 5)
        self.assertRaises(ValueError, dataStructure.getDataEntry, [], [], [])

    def test_getDataEntry_broken_path(self):
        data = None
        dataStructure = DataStructure(self.dataManager, 5)
        self.assertRaises(ValueError, dataStructure.getDataEntry, data,
                          ['a', 'b'], [Exception(), ...])

    def test_getDataEntry_invalid_indices_type(self):
        dataStructure = DataStructure(self.dataManager, 5)
        dataStructure.createEntry('parameters', DataEntry('parameters',3))
        data = None
        self.assertRaises(ValueError, dataStructure.getDataEntry,data,
            ['parameters'], 'x')

    def test_setDataEntry_empty_path(self):
        dataStructure = DataStructure(self.dataManager, 5)
        data = None
        self.assertRaises(ValueError, dataStructure.setDataEntry, data, [], [],
                          np.ndarray((1, 2)))

    def test_setDataEntry_invalid_data_shape(self):
        dataStructure = DataStructure(self.dataManager, 5)
        data = None
        self.assertRaises(ValueError, dataStructure.setDataEntry, data, ['a'],
                          [slice(0, 5)], np.ndarray((1, 2)))

        self.assertRaises(ValueError, dataStructure.setDataEntry, data, ['a'],
                          [3], np.ndarray((2, 1)))

    def test_setDataEntry_invalid_indice_type(self):
        dataStructure = DataStructure(self.dataManager, 5)
        data = None
        self.assertRaises(ValueError, dataStructure.setDataEntry, data, ['a'],
                          [Exception()], np.ndarray((2, 1)))



if __name__ == '__main__':
    unittest.main()
