class DataEntry():
    '''
    DataEntry stores the properties of a data entry.
    '''

    def __init__(self, name, size, minValue, maxValue):
        '''Constructor'''
        self.name = name
        self.size = size
        self.minValue = minValue
        self.maxValue = maxValue
