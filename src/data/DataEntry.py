class DataEntry():
    '''
    DataEntry stores the properties of a data entry.
    '''

    def __init__(self, name, numDimensions, minRange, maxRange):
        '''Constructor'''
        self.name = name
        self.numDimensions = numDimensions
        self.minRange = minRange
        self.maxRange = maxRange
