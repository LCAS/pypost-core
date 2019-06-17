
def build_dict(unconstrained, opt_dict=None):
    if opt_dict is None:
        opt_dict = dict()
    opt_dict['disp'] = unconstrained.verbose
    opt_dict['maxiter'] = unconstrained.maxNumOptiIterations
    opt_dict['maxfev'] = unconstrained.maxNumOptiEvaluations
    opt_dict['xtol'] = unconstrained.optiAbsxTol
    opt_dict['ftol'] = unconstrained.optiAbsfTol
    opt_dict['epsilon'] = unconstrained.epsilon
    return opt_dict

