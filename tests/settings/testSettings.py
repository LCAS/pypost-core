import unittest
from common.Settings import Settings
from common import SettingsManager
from common.SettingsClient import SettingsClient

class testSettings(unittest.TestCase):
    '''Tests Settings, SettingsManager, SettingsClient from common
    '''

    def test_setProperty(self):
        self.assertEqual(SettingsManager.inDebugMode(), False)
        SettingsManager.activateDebugMode()
        self.assertEqual(SettingsManager.inDebugMode(), True)
        SettingsManager.deactivateDebugMode()
        self.assertEqual(SettingsManager.inDebugMode(), False)

        settings = Settings('testSettings01')
        SettingsManager.setSettings(settings)
        cli = SettingsClient()
        cli.setVar('prop_a', 42.21)
        cli.linkProperty('prop_a', 'A', SettingsManager.getSettings('testSettings01'))
        self.assertIs(SettingsManager.getSettings('testSettings01'), settings)
        self.assertEqual(SettingsManager.getSettings('testSettings01').getProperty('A'), 42.21)
        self.assertEqual(cli.settingsClientName[:-3], 'client_')

        SettingsManager.pushDefaultName('standard')
        self.assertEqual(SettingsManager.getDefaultName(), 'standard')
        self.assertEqual(SettingsManager.getDefaultSettings().name, 'standard')

        self.assertEqual(SettingsManager.getRootName(), 'default')

        SettingsManager.popDefaultName()
        self.assertEqual(SettingsManager.getDefaultName(), 'default')
        SettingsManager.popDefaultName()
        self.assertEqual(SettingsManager.getDefaultName(), 'default')

        cli.setVar('prop_b', False)
        cli.linkProperty('prop_b', 'B')
        self.assertEqual(SettingsManager.getDefaultSettings().getProperty('B'), False)

        cli.setVar('prop_c', 'testStr')
        cli.linkProperty('prop_c')
        self.assertEqual(SettingsManager.getDefaultSettings().getProperty('prop_c'), 'testStr')

        clonedSettings = SettingsManager.cloneSettings(settings, 'clonedSettings')
        self.assertEqual(clonedSettings.getProperty('A'), 42.21)
        self.assertEqual(clonedSettings.name, 'clonedSettings')
        emptySettings = SettingsManager.cloneSettings(None, 'emptySettings')
        self.assertDictEqual(emptySettings._properties, {})
        cSettings = SettingsManager.cloneSettings(emptySettings, 'testSettings01')
        self.assertEqual(cSettings.getProperty('A'), 42.21)

        SettingsManager.delSettings('notExistant')
        self.assertIsNotNone(SettingsManager.getSettings('testSettings01'))
        SettingsManager.delSettings('testSettings01')
        self.assertIsNone(SettingsManager.getSettings('testSettings01'))

        settings.registerProperty('A', 84.42)
        self.assertEqual(settings.getProperty('A'), 84.42)
        settings.setToClients()
        self.assertEqual(cli.getVar('prop_a'), 84.42)

        self.assertDictEqual(settings.getProperties(), {'A': 84.42})

        settings.registerProperty('D', 17)
        settings.setProperty('D', 97)
        self.assertEqual(settings.getProperty('D'), 97)

        settings.setIfEmpty('E', (2, 7))
        self.assertEqual(settings.getProperty('E'), (2, 7))
        settings.setIfEmpty('E', (3, 22))
        self.assertEqual(settings.getProperty('E'), (2, 7))

        clonedSettings.setProperties(settings.getProperties())
        self.assertDictEqual(clonedSettings.getProperties(), settings.getProperties())
        self.assertTrue(clonedSettings.hasValue('D', 97))
        self.assertTrue(clonedSettings.hasProperty('E'))

        cli.setVar('prop_d', 13)
        cli.linkProperty('prop_d', 'D', emptySettings)
        emptySettings.copyProperties(settings)
        dClis = emptySettings._properties['D'].clients
        self.assertEqual(emptySettings.getProperty('D'), 97)
        self.assertListEqual(emptySettings._properties['D'].clients, dClis)
        self.assertEqual(emptySettings.getProperty('A'), 84.42)

        cli.setVar('prop_e', 2)
        cli.linkProperty('prop_e', 'E', clonedSettings)
        self.assertEqual(cli.getVar('prop_e'), (2, 7))

        self.assertIsNone(settings.getProperty('nonExistent'))

        self.assertSetEqual(settings.getDifferentProperties(clonedSettings), set())

        try:
            settings.informClients('noProp')
        except KeyError:
            self.fail("Unhandled KeyError in Settings.informClients()!")

        settings.removeClients()
        self.assertListEqual(settings._properties['A'].clients, [])

        settings.unregisterProperty('E')
        self.assertIsNone(settings.getProperty('E'))

        try:
            settings.unregisterProperty('E')
        except KeyError:
            self.fail("Unhandled KeyError in Settings.unregisterProperty()!")

        settings.clean()
        self.assertDictEqual(settings._properties, {})


        print("Client Properties:")
        cli.printProperties()
        print("\nClonedSettings Properties:")
        clonedSettings.printProperties()

    def test_settings_clone(self):
        settings = Settings('testSettings1')
        settings.setProperty('testProp1', 41)
        SettingsManager.setSettings(settings)
        cli = SettingsClient()
        cli.setVar('testProp2', 42)

        settings2 = settings.clone('newSettings')
        settings2.setProperty('testProp3', 43)

        self.assertEqual(settings2.getProperty('testProp1'), 41)
        self.assertEqual(cli.getVar('testProp2'), 42)
        self.assertEqual(settings2.getProperty('testProp3'), 43)


    def test_settings_store_load(self):
        settings = Settings('testSettings1')
        settings.setProperty('testProp1', 42)
        SettingsManager.setSettings(settings)
        cli = SettingsClient()
        cli.test2 = 42
        cli.linkProperty('test2', 'testProp2', settings)

        settings.store('/tmp/rlt-test.settings')
        settings.setProperty('testProp2', 8)
        settings2 = Settings('testSettings2')
        settings2.setProperty('testProp1', 9)
        settings.load('/tmp/rlt-test.settings')

        self.assertEqual(settings.getProperty('testProp1'), 42)
        self.assertEqual(settings2.getProperty('testProp1'), 9)

        # FIXME: check if globalProperties should be stored to disk
        self.assertEqual(cli.getVar('test2'), 8)

if __name__ == "__main__":
    unittest.main()
