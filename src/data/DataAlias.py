class DataAlias():
    '''
    DataAliases are subsets or concatinations of DataEntries.
    '''

    def __init__(self, aliasName, entryNames, indexList):
        '''
        @param aliasName The name of the alias
        @param entryNames A list of entrieNames the alias should point to
        @param indexList A list of slices that correspond to the list
                         of entryNames
        '''
        self.aliasName = aliasName
        self.entryNames = entryNames
        self.indexList = indexList

        # assert len(indexlist) == len(entryNames)

    def __getitem__(self, k):
        # Overwrite the getter
        # TODO: get data from the right data entry
        return 42

    def __setitem__(self, k, v):
        # Overwrite the setter
        # TODO: store the data in the right data entry
        return 42
