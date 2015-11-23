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
