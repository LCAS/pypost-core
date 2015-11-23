class DataAlias():
    '''
    DataAliases are subsets or concatinations of DataEntries.
    '''

    def __init__(self, aliasName, entryList):
        '''
        @param aliasName The name of the alias
        @param entryList A list of entry names and the corresponding slices
                         the alias should point to, e.g.
                         {'param': slice(1,5,2), 'param2': slice(-3)}
        '''
        self.aliasName = aliasName
        self.entryList = entryList

        for key, value in entryList.items():
            print(key, value)

        # assert len(indexlist) == len(entryNames)

    def __getitem__(self, k):
        # Overwrite the getter
        # TODO: get data from the right data entry
        return 42

    def __setitem__(self, k, v):
        # Overwrite the setter
        # TODO: store the data in the right data entry
        return 42
