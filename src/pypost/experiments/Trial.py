from pypost.common.Settings import Settings
from pypost.common import SettingsManager
import numpy as np
from enum import Enum
from pypost.common.SettingsClient import SettingsClient
import yaml, subprocess, os, time, random, os.path
import fasteners  # module for file based mutex handling, pip3 install fasteners
import git  # used for parsing git revisions, pip3 install gitpython
from os.path import join as join_path
from contextlib import contextmanager

class TrialStoringType(Enum):
    STORE = 1
    STORE_PER_ITERATION = 2
    ACCUMULATE = 3
    ACCUMULATE_PER_ITERATION = 4


class Trial(SettingsClient):

    def __init__(self, evalDir, index, trialSettings=None):
        # Creates the required directories
        super().__init__()
        if os.path.isdir(evalDir):
            self.trialDir = join_path(evalDir, 'trial%03d' % index)
            if not os.path.exists(self.trialDir):
                os.mkdir(self.trialDir)
                os.chmod(self.trialDir, 0o775)
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
        self.gitRevisionNumber = -1
        random.seed(index)
        self.rngState = random.getstate()
        self.numIterations = 0
        self.loaded = False

    def nextIteration(self):
        self.numIterations = self.numIterations + 1

    def file_path(self, name, trial_dir=None):
        return join_path(trial_dir or self.trialDir, name)

    @contextmanager
    def get_lock(self, file_path, timeout=0.1):
        lock = fasteners.InterProcessLock(file_path)
        success = lock.acquire(timeout=timeout)
        if not success:
            raise TimeoutError("Couldn't acquire lock for %s" % file_path)
        yield
        lock.release()

    def read_write_lock(self, trial_dir=None, timeout=0.1):
        return self.get_lock(join_path(trial_dir or self.trialDir, 'trial_rw.lock'), timeout)

    def run_lock(self, trial_dir=None, timeout=0.1):
        return self.get_lock(join_path(trial_dir or self.trialDir, 'trial_run.lock'), timeout)

    def store(self, name, value):
        ''' Stores a piece of data. Multiple storage options are available.
        :param name: The name under which the data is stored
        :param value: The data
        :param mode: Can be either one of STORE_PER_ITERATION,
                     ACCUMULATE_PER_ITERATION, STORE, ACCUMULATE
        '''

        if name in self.data:
            self.data[name] = np.vstack((self.data[name], value))
            self.data["_t_" + name].append(time.time())
        else:
            self.data[name] = value
            self.data["_t_" + name] = [time.time()]

    def storeTrial(self, overwrite=True):
        return self.storeTrialInFile(self.trialDir, overwrite)

    def storeTrialInFile(self, trialDir, overwrite=True):
        ''' Stores the trial in the given directory. Data and settings are stored separately.
        :param string filename: File name
        :param bool overwrite: Overwrite
        :return: True if storing is successful, False otherwise
        :rtpye: bool
        '''

        if trialDir is None or not os.path.isdir(trialDir):
            return False

        try:
            with self.read_write_lock(trialDir, timeout=0.5):
                data_path, settings_path, trial_path = (join_path(trialDir, name) for name in
                                                        ('data.npy', 'settings.yaml', 'trial.yaml'))

                if not overwrite and True in (os.path.isfile(f) for f in (data_path, settings_path, trial_path)):
                    return False

                np.save(data_path, self.data)
                self.trialSettings.store(settings_path)
                trialDict = dict(isFinished=self.isFinished, rngState=self.rngState,
                                 gitRevisionNumber=self.gitRevisionNumber, numIterations=self.numIterations)
                with open(trial_path, 'w') as stream:
                    yaml.dump(trialDict, stream, default_flow_style=False)
                return True
        except TimeoutError:
            print("unable to acquire mutex for storing trial")
            return False

    def loadTrial(self):
        self.loadTrialFromFile(self.trialDir)

    def loadTrialFromFile(self, trialDir):
        '''  Loads a trial from the given directory.
        :param trialDir: The directory of the trial to load '''

        settings_path, data_path = (join_path(trialDir, f) for f in ('settings.yaml', 'data.npy'))
        print("Loading trial %s" % trialDir)

        if not os.path.isdir(trialDir):
            raise FileNotFoundError("Trial directory does not exist")
        if not os.path.isfile(settings_path):
            raise FileNotFoundError("Settings file not found")
        if not os.path.isfile(data_path):
            raise FileNotFoundError("Data file not found")

        self.trialSettings.load(settings_path)
        self.settings.copyProperties(self.trialSettings)
        # resolve numpy crazyness with storing dictionary (wraps around and array)
        temp = np.load(data_path)
        self.data = temp[()]

        with self.read_write_lock(trialDir, timeout=0.5):
            with open(join_path(trialDir, 'trial.yaml'), 'r') as f:
                trialDict = yaml.load(f)

            self.isFinished = trialDict['isFinished']
            self.rngState = trialDict['rngState']
            self.gitRevisionNumber = trialDict['gitRevisionNumber']
            self.numIterations = trialDict['numIterations']
        self.loaded = True

    def start(self, restart=0):
        try:
            with self.run_lock():
                if not self.loaded:
                    self.loadTrial()
                if self.isFinished and not restart == -2:
                    print("Trial %s is already finished!" % self.trialDir)
                else:
                    SettingsManager.setRootSettings(self.settings)
                    date = time.strftime('%Y/%m/%d_%H:%M')
                    try:
                        commit = git.Repo(search_parent_directories=True).head.commit
                        self.gitRevisionNumber = str(commit.count()) + ':' + commit.hexsha + ':' + date
                    except git.exc.InvalidGitRepositoryError:
                        self.gitRevisionNumber = date

                    random.setstate(self.rngState)
                    self.configure()
                    self.run()
                    self.isFinished = True
                    self.storeTrial()
        except TimeoutError:
            print("Trial %s is already running!" % self.trialDir)

    def applyTrialSettings(self):
        self.settings.copyProperties(self.trialSettings)

    def configure(self):
        SettingsManager.pushDefaultSettings(self.settings)
        self._configure()
        SettingsManager.popDefaultSettings()

    def _configure(self):
        raise NotImplementedError("Must be overwritten by subclass")  # pragma: no cover

    def run(self):
        SettingsManager.pushDefaultSettings(self.settings)
        self._run()
        SettingsManager.popDefaultSettings()

    def _run(self):
        raise NotImplementedError("Must be overwritten by subclass")  # pragma: no cover
