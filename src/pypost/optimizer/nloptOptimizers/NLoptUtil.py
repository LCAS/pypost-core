
def getReturnMessage(returnCode):
    if   returnCode ==  1:  return 'optimization successful'
    elif returnCode ==  2:  return 'optimization successful: \'stopval\' was reached'
    elif returnCode ==  3:  return 'optimization successful: \'ftol\' was reached'
    elif returnCode ==  4:  return 'optimization successful: \'xtol\' was reached'
    elif returnCode ==  5:  return 'optimization successful: \'maxeval\' was reached'
    elif returnCode ==  6:  return 'optimization successful: \'maxtime\' was reached'
    elif returnCode == -1:  return 'optimization failed'
    elif returnCode == -2:  return 'optimization failed: invalid arguments'
    elif returnCode == -3:  return 'optimization failed: out of memory'
    elif returnCode == -4:  return 'optimization failed: roundoff errors limited progress'
    elif returnCode == -5:  return 'optimization failed: forced termination'
    else:                   return 'unknown return code'

def usesGradient(optimizer):
    name = optimizer.get_algorithm_name()
    if 'no-derivative' in name:
        return False
    else:
        return True


