class DataEntry():
    '''
    DataEntry stores the properties of a data entry.
    '''

    def __init__(self, name, size, minRange, maxRange):
        '''Constructor'''
        self.name = name
        self.size = size
        self.minRange = minRange
        self.maxRange = maxRange
