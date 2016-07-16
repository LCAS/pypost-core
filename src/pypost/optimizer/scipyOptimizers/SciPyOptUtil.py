from pypost.optimizer.Unconstrained import Unconstrained
import warnings

def build_dict(unconstrained, opt_dict=None):
    if opt_dict is None:
        opt_dict = dict()
    opt_dict['disp'] = unconstrained.verbose
    opt_dict['maxiter'] = unconstrained.maxNumOptiIterations
    opt_dict['xtol'] = unconstrained.optiAbsxTol
    opt_dict['ftol'] = unconstrained.optiAbsfTol
    opt_dict['epsilon'] = unconstrained.epsilon
    return opt_dict

def suppress_warnings():
    warnings.filterwarnings('ignore', '.*Unknown solver options:*.')
    warnings.filterwarnings('ignore', '.*does not use Hessian information*.')

algorithms = ['Nelder-Mead',
              'Powell',
              'GC',
              'BFGS',
              'Newton-GC',
              'L-BFGS-B',
              'TNC',
              'COBLYA',
              'SLSQP',
              'dogleg',
              'trust-ncg']

box_const_algos = ['L-BFGS-B',
                   'TNC',
                   'SLSQP']

