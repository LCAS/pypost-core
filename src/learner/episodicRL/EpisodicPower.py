'''
Created on 22.01.2016

@author: Moritz
'''

class EpisodicPower(RLByWeightedML, object):
    '''
    Power Algorithm
    '''


    def __init__(self, policyLearner, args**):
        '''
        Constructor
        '''
        