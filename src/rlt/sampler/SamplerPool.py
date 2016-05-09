class SamplerPool(object):
    '''
    A collection of samplers

    Methods (annotated):
    def __init__(self, name: str, priority: int) -> None
    def getName(self) -> str
    def _setName(self, name: str) -> None
    def getPriority(self) -> int
    def _setPriority(self, priority: int) -> None
    def flush(self) -> None
    '''

    def __init__(self, name, priority):
        '''
        Creates a sampler pool with an empty sampler list
        '''
        self.samplerList = []
        '''
        List containing the samplers
        '''
        self._setName(name)
        self._setPriority(priority)

    # getters & setters

    def getName(self):
        return self._name

    def _setName(self, name):
        self._name = name

    def getPriority(self):
        return self._priority

    def _setPriority(self, priority):
        '''
        :change: only positive priorities are allowed [0,...]
        '''
        if priority < 0:
            raise RuntimeError("Priority has to be greater or equal to zero")
        self._priority = priority

    def flush(self):
        '''
        Clear all samplers in this pool
        '''
        self.samplerList.clear()
