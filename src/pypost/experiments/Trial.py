from pypost.common.Settings import Settings
from pypost.common import SettingsManager
import numpy as np
from enum import Enum
from pypost.common.SettingsClient import SettingsClient
import yaml, subprocess, os, time, random, os.path


class TrialStoringType(Enum):
    STORE = 1
    STORE_PER_ITERATION = 2
    ACCUMULATE = 3
    ACCUMULATE_PER_ITERATION = 4


class Trial(SettingsClient):

    def __init__(self, evalDir, index, trialSettings = None):
        '''
        Constructor
        Creates the required directories
        '''
        super().__init__()
        configured = False

        if os.path.isdir(evalDir):
            self.trialDir = os.path.join(evalDir, 'trial%03d' % index)
            if not os.path.exists(self.trialDir):
                os.mkdir(self.trialDir)
                os.chmod(self.trialDir, 0o775)
            logFile = os.path.join(self.trialDir, 'trial.log')
            os.close(os.open(logFile, os.O_CREAT | os.O_APPEND))
            os.chmod(logFile, 0o664)
        else:
            print("Trial %s: Directory not found" % evalDir)
            self.trialDir = None

        self.index = index
        self.data = {}

        if trialSettings is None:
            self.trialSettings = Settings('trialSettings')
        else:
            self.trialSettings = trialSettings.clone()

        self.settings = Settings('trialSettings')

        self.isFinished = False
        self.isRunning = False
        self.gitRevisionNumber = -1
        random.seed(index)
        self.rngState = random.getstate()

        self.hasLock = False
        self.numIterations = 0

    def nextIteration(self):
        self.numIterations = self.numIterations + 1

    def store(self, name, value):
        '''
        Stores a piece of data. Multiple storage options are available.
        :param name: The name under which the data is stored
        :param value: The data
        :param mode: Can be either one of STORE_PER_ITERATION,
                     ACCUMULATE_PER_ITERATION, STORE, ACCUMULATE
        '''

        if (name in self.data):
            self.data[name] = np.vstack((self.data[name], value))
        else:
            self.data[name] = value

    def storeTrial(self, overwrite=True):
        return self.storeTrialInFile(self.trialDir, overwrite)

    def storeTrialInFile(self, trialDir, overwrite=True):
        '''
        Stores the trial in the given directory.
        Data and settings are stored separately.
        :param string filename: File name
        :param bool overwrite: Overwrite
        :return: True if storing is successful, False otherwise
        :rtpye: bool
        '''

        if trialDir is None or not os.path.isdir(trialDir):
            return False

        dataFile = os.path.join(trialDir, 'data.npy')

        if overwrite or not os.path.isfile(dataFile):
            np.save(dataFile, self.data)
        else:
            return False

        settingsFile = os.path.join(trialDir, 'settings.yaml')

        if overwrite or not os.path.isfile(settingsFile):

            self.trialSettings.store(settingsFile)

        else:
            return False

        trialFile = os.path.join(trialDir, 'trial.yaml')
        trialDict = dict()

        trialDict['isFinished'] = self.isFinished
        trialDict['isRunning'] = self.isRunning
        trialDict['rngState'] = self.rngState
        trialDict['gitRevisionNumber'] = self.gitRevisionNumber
        trialDict['numIterations'] = self.numIterations

        lockedFile = self.lockFile()
        if overwrite or not os.path.isfile(trialFile):
            with open(trialFile, 'w') as stream:
                yaml.dump(trialDict, stream)

            if (lockedFile):
                self.unlockFile()
            return True
        else:
            if (lockedFile):
                self.unlockFile()
            return False


    def loadTrial(self):
        self.loadTrialFromFile(self.trialDir)

    def loadTrialFromFile(self, trialDir):
        '''
        Loads a trial from the given directory.
        :param trialDir: The directory of the trial to load
        '''
        print("Loading trial %s" % trialDir)
        if not os.path.isdir(trialDir):
            raise FileNotFoundError("Trial directory does not exist")
        settingsFile = os.path.join(trialDir, 'settings.yaml')
        dataFile = os.path.join(trialDir, 'data.npy')
        if not os.path.isfile(settingsFile):
            raise FileNotFoundError("Settings file not found")
        if not os.path.isfile(dataFile):
            raise FileNotFoundError("Data file not found")
        self.trialSettings.load(settingsFile)
        self.settings.copyProperties(self.trialSettings)
        # resolve numpy crazyness with storing dictionary (wraps around and array)
        temp = np.load(dataFile)
        self.data = temp[()]

        trialFile = os.path.join(trialDir, 'trial.yaml')

        lockedFile = self.lockFile()
        with open(trialFile, 'r') as stream:
            trialDict = yaml.load(stream)
        self.isFinished = trialDict['isFinished']
        self.isRunning = trialDict['isRunning']
        self.rngState = trialDict['rngState']
        self.gitRevisionNumber = trialDict['gitRevisionNumber']
        self.numIterations = trialDict['numIterations']

        if (lockedFile):
            self.unlockFile()


    def lockFile(self):
        if (self.hasLock):
            return False
        lockFile = os.path.join(self.trialDir, 'trial.lock')

        while True:
            if not os.path.exists(lockFile):
                lock = open(lockFile, 'w')
                self.hasLock = True
                break

            else:
                check = os.stat(lockFile)
                if time.time() - check.st_ctime > 1:
                    os.remove(lockFile)
                print('waiting my turn for opening trial {0}'.format(self.trialDir))
                time.sleep(0.5)
        return True

    def unlockFile(self):
        lockFile = os.path.join(self.trialDir, 'trial.lock')
        os.remove(lockFile)
        self.hasLock = False

    def start(self, restart = 0):
        self.lockFile()
        self.loadTrial()
        if self.isFinished and not restart == -2:
            print("Trial %s is already finished!" % self.trialDir)
            self.unlockFile()
        elif (self.isRunning and not restart <= -1):
            print("Trial %s is already running!" % self.trialDir)
            self.unlockFile()
        else:
            SettingsManager.setRootSettings(self.settings)

            commitCount = subprocess.getoutput(["git rev-list --count HEAD"])
            revNumber = subprocess.getoutput(["git rev-list --full-history --all | head -1"])
            date = time.strftime('%Y/%m/%d_%H:%M')

            self.gitRevisionNumber = commitCount + ':' + revNumber + ':' + date
            self.isRunning = True
            self.storeTrial()
            self.unlockFile()

            random.setstate(self.rngState)

            self.configure()
            self.run()

            self.isFinished = True
            self.storeTrial()

    def applyTrialSettings(self):
        self.settings.copyProperties(self.trialSettings)

    def configure(self):
        SettingsManager.pushDefaultSettings(self.settings)
        self._configure()
        SettingsManager.popDefaultSettings()

    def _configure(self):
        raise NotImplementedError("Must be overwritten by subclass") # pragma: no cover

    def run(self):
        SettingsManager.pushDefaultSettings(self.settings)
        self._run()
        SettingsManager.popDefaultSettings()


    def _run(self):
        raise NotImplementedError("Must be overwritten by subclass")  # pragma: no cover
