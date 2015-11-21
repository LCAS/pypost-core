'''
Created on 21.11.2015

@author: Moritz
'''
from src.interfaces.SamplerInterface import SamplerInterface
from scipy import Inf
from src.sampler.SamplerPool import SamplerPool

class Sampler(object, SamplerInterface):
    '''
    Sampler serves as a base class for all other samplers. But you should consider using the subclasses SequentialSampler,
    IndependentSampler or for a learning scenario EpisodeSampler or EpisodeWithStepSampler.
    
    Every sampler models a sampling scenario. Various sampler pools will be used to handle action policy, simulating the environment,
    rewards and such. Each of those pools may contain a number of sampler functions
    acting on a given Data.Data structure. The task of the sampler is organizing those pools and their execution.  
    '''
    
    # attributes
    
    def __init__(self, dataManager, samplerName):
        '''
        Constructor
        '''
        
        super(SamplerInterface, self).__init__();
        
        self._samplerPools={}
        '''
        All functions in a given pool
        '''
        self._samplerName=samplerName
        '''
        String of the sampler name
        #CHANGE now holds samplerPool instances instead of their names
        '''
        self._samplerPoolPriorityList=[]
        '''
        List of all pools ordered by priority
        '''
        self._samplerMap={}
        '''
        List of lower level samplers after finalizing the sampler
        '''
        self._iterationIndex
        '''
        Index of the current iteration
        '''
        self._lowerLevelSamplers=[]
        '''
        List of lower level samplers
        '''
        
    
    # getters & setters

    def _setSamplerName(self, samplerName):
        self._samplerName=samplerName
    
    def getSamplerName(self):
        return self._samplerName
    
    # functions
    
    def setSamplerIteration(self, iteration):
        self.iterationIndex=iteration
    
    #ASK is this function necessary?
    #def getDataManagerFromSampler(self):
    #    return self.datamanager;
    
    #CHANGE finalizeData is no longer optional
    def finalizeSampler(self, finalizeData):
        lowLevelsamplers=self.getLowLevelSamplers()
        for samplerName in lowLevelsamplers.getKeys():
            sampler=lowLevelsamplers[samplerName]
            if sampler in self.lowLevelsamplers:
                raise RuntimeError("Added already added lower-level sampler \""+samplerName+"\"")
            sampler.finalizeSampler(False)
            self._samplerMap[sampler.getsamplerName()]=sampler
        
        if finalizeData:
            self._dataManager.finalizeDataManager()
    
    def copyPoolsFromSampler(self, sampler):
        self._samplerPools=sampler._samplerPools.copy()
        self._samplerPoolPriorityList=sampler._samplerPoolPriorityList.copy()
        #ASK the line below was commented out in matlab code is there a reason for that? ^mw
        #self._lowerLevelSamplers=sampler.lowerLevelSamplers
        self._samplerMap=sampler._samplerMap
    
    def copySamplerFunctionsFromPool(self,sampler,poolName):
        '''
        Copies all sampler functions from 'poolName' in sampler
        to to sample pool in 'this' sampler
        '''
        self._samplerPools[poolName]=sampler._samplerPools[poolName]
    
    def isSamplerFunction(self, samplerName):
        if self.getSamplerName()==samplerName:
            return True
        else:
            return super(DataManipulatorInterface,self).isSamplerFunction(samplerName)
    
    def callDataFunction(self,samplerName,newData,*args):
        if self.getSamplerName()==samplerName:
            self._createSamples(newData, args)
        else:
            super(DataManipulatorInterface,self).callDataFunction(samplerName,newData,args)
    
    #CHANGE we explicitly require a sampler pool in case the pool class will be altered in the future
    def addSamplerPool(self, samplerPool):
        '''
        Adds a sampler pool to the sampler pool list
        
        @throws If a sampler pool with the same name already exists
        @throws If a sampler pool with the same priority already exists 
        '''
        if samplerPool.getName() in self._samplerPools.keys():
            raise RuntimeError("A sampler pool with the name \""+samplerPool.getName()+"\" already exists")
        
        self._samplerPools[samplerPool.getName()]=samplerPool
        
        #add sampler to priority list 
        index=0
        for idx,pool in enumerate(self._samplerPoolPriorityList):
            if samplerPool.getPriority()==pool.getPriority():
                raise RuntimeError("A sampler pool with the same priority already exists")
            
            if samplerPool.getPriority()>pool.getPriority():
                index=idx
                break
        
        self._samplerPoolPriorityList.insert(index, samplerPool)
        
    #CHANGE flushSamplerPool got deleted. Call samplerPool[name].flush()
        
    def addLowerLevelSampler(self, samplerPool,lowerLevelSampler,isBeginning):
        self.addSamplerFunction(samplerPool, lowerLevelSampler, isBeginning)
        self._lowerLevelSamplers.append(lowerLevelSampler)

    #ASK unify names as low- or lowerLevelSamplers?
    def getLowerLevelSamplers(self):
        '''
        get all recursively invoked lower-level samplers
        @return: list of all lower-level samplers
        '''
        
        lowerLevelSamplersRecursive=self._lowerLevelSamplers.copy()
        #we iterate breadth-first by adding new lower-level iterators to the end of the list
        for sampler in self._lowerLevelSamplers:
            lowerLevelSamplersRecursive.extend(sampler.getLowerLevelSamplers());
        
        return lowerLevelSamplersRecursive
    
    def addSamplerFunctionToPool(self,samplerPool,samplerName,objHandle,addLocationFlag):
        '''
        #FIXME bad design?
        #FIXME only allow 1
        #CHANGE addLocationFlag is no longer optional
        Add a function or sampler to a sampler pool
        
        The function behaves differently for different values of addLocationFlag  
        -1 will add the new samplerfunction to the beginning of the sampler pool
        0 will flush the entire sampler pool and only add samplerPool afterward
        1 will add the new sampler function at the end of the sampler pool.
        
        
        @param samplerPool: sampler pool to whom the sampler function will be included
        @param samplerName: name of the new sampler function
        @param objHandle: function handle of the new sampler function
        @param addLocationFlag: Determines to determines the behaviour of the function.
        
        '''
        if not self.isSamplerFunction(samplerName):
            raise RuntimeError(samplerName+" is not a valid sampler function of the object")
        
        #ASK sampleFunction was never as an object in Matlab, is this the default behaviour? 
        sampleFunction={}
        sampleFunction.samplerName=samplerName
        sampleFunction.objHandle=objHandle
        
        def case0(self):
            self._samplerPools[samplerName].samplerList.insert(0,sampleFunction)
        def case1(self):
            self._samplerPools[samplerName].clear()
            self._samplerPools[samplerName].append()
        def case2(self):
            self._samplerPools[samplerName].append()
        switch={
            0: case0,
            1: case1,
            2: case2 
        }
        switch[addLocationFlag](self);
            
    def createSamplesFromPool(self,pool,data,*args):
        '''
        executes all functions on the samplerList of a given pool
        
        @param poolName: name of the selected pool
        @param data: the data structure the pool operates on
        @param args: hierarchical indexing of the data structure
        '''
        for sampler in pool.samplerList:
            objectPointer=sampler.objHandle
            objectPointer.callDataFunction(sampler.getName(),data,args)

    def sampleAllPools(self,data,*args):
        '''
        Samples all pools
        
        @param newData: the data structure the pool operates on
        @param *args: hierarchical indexing of the data structure
        '''
        for pool in self._samplerPoolPriorityList:
            self.createSamplesFromPool(pool,data, args)        
    
    def createSamplesFromPoolWithPriority(self,lowPriority,highPriority,data,*args):
        '''
        Samples all pools in a specific priority range
        
        @param lowPriority: lower bound of pools that will be executed
        @param highPriority: higher bound of pools that will be executed
        @param newData: the data structure the pool operates on
        @param *args: hierarchical indexing of the data structure
        '''
        for pool in self._samplerPoolPriorityList:
            if pool.getPriority()>=lowPriority:
                #break if we exceed to upper bound
                if pool.getPriority()>highPriority:
                    break
                self.createSamplesFromPool(pool,data, args)
        
    #TASK where was _addSamplerToPoolInternal used?
    #ASK addSamplerFunction referenced in MatLab code does not exists
    #CHANGE removed _addSamplerToPoolInternal






















