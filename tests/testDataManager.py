import unittest
import sys

sys.path.append( '../src/data' )
from DataManager import DataManager

class testDataManager(unittest.TestCase):
  def test_init(self):
      print(self)
      dataManager = DataManager('episodes')
      self.assertIsInstance(dataManager, DataManager)
      self.assertEqual(dataManager.name, 'episodes')

  def test_subDataManager(self):
      dataManager = DataManager('episodes')
      subDataManager = DataManager('steps')
      subSubDataManager = DataManager('subSteps')

      dataManager.subDataManager = subDataManager
      subDataManager.subDataManager = subSubDataManager

      self.assertIs(dataManager.subDataManager, subDataManager)
      self.assertIs(dataManager.subDataManager.subDataManager, subSubDataManager)

  def test_split(self):
      s = 'hello world'
      self.assertEqual(s.split(), ['hello', 'world'])
      # check that s.split fails when the separator is not a string
      with self.assertRaises(TypeError):
          s.split(2)

if __name__ == '__main__':
    unittest.main()
