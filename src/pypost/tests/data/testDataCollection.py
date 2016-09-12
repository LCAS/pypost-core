import unittest
from pypost.data.DataCollection import DataCollection

class testDataCollection(unittest.TestCase):

    def test_init_givenNoStandardData_expectNoException(self):
        dataCollection = DataCollection()

        self.assertIsInstance(dataCollection, DataCollection)
        self.assertEqual(dataCollection.getStandardDataName(), "data")
        self.assertEqual(dataCollection.getStandardData(), None)

    def test_init_givenStandardData_expectNoException(self):
        data = [1, 2, 3, 4]
        dataCollection = DataCollection(data)

        self.assertIsInstance(dataCollection, DataCollection)
        self.assertEqual(dataCollection.getStandardData(), data)

    def test_setStandardData_givenData_expectGivenInputData(
            self):
        data = [1, 2, 3, 4]
        dataCollection = DataCollection()
        dataCollection.setStandardData(data)

        self.assertEqual(dataCollection.getStandardData(), data)

    def test_getStandardData_givenData_expectGivenInputData(
            self):
        data = [1, 2, 3, 4]
        dataCollection = DataCollection()
        dataCollection.setStandardData(data)

        self.assertEqual(dataCollection.getStandardData(), data)

    def test_setDataObject_givenData_expectGivenInputData(
            self):
        data = [1, 2, 3, 4]
        dataCollection = DataCollection()
        dataCollection.setDataObject(data,"test")

        self.assertEqual(dataCollection.getDataObject("test"), data)

    def test_setDataObject_givenEmptyName_expectException(
            self):
        data = [1, 2, 3, 4]
        dataCollection = DataCollection()
        self.assertRaises(
            RuntimeError, lambda: dataCollection.setDataObject(data,""))

    def test_getDataObject_givenData_expectGivenInputData(
            self):
        data = [1, 2, 3, 4]
        dataCollection = DataCollection()
        dataCollection.setDataObject(data, "test")

        self.assertEqual(dataCollection.getDataObject("test"), data)

    def test_getDataObject_givenEmptyName_expectException(
            self):
        dataCollection = DataCollection()

        self.assertRaises(
            KeyError, lambda: dataCollection.getDataObject(""))

    def test_getDataObject_givenNonExistingName_expectException(
            self):
        dataCollection = DataCollection()

        self.assertRaises(
            KeyError, lambda: dataCollection.getDataObject("noExisting"))

    def test_setStandardDataName_givenValidName_expectGivenName(
            self):
        dataCollection = DataCollection()
        dataCollection.setStandardDataName("testName")

        self.assertEqual(dataCollection.getStandardDataName(), "testName")

    def test_setStandardDataName_givenEmptyName_expectException(
            self):
        dataCollection = DataCollection()
        self.assertRaises(
            RuntimeError, lambda: dataCollection.setStandardDataName(""))

    def test_getStandardDataName_givenDefaultName_expectDefaultName(
            self):
        dataCollection = DataCollection()

        self.assertEqual(dataCollection.getStandardDataName(), "data")

    def test_getStandardDataName_givenValidName_expectGivenName(
            self):
        dataCollection = DataCollection()
        dataCollection.setStandardDataName("testName")

        self.assertEqual(dataCollection.getStandardDataName(), "testName")

if __name__ == '__main__':
    unittest.main()
