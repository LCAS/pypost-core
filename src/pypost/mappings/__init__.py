from .Mapping import Mapping
from .TFMapping import TFMapping
from .Function import Function_Base
from .Function import LinearFunction
from .Gaussian import DiagonalGaussian_Base
from .Gaussian import ConstantDiagionalGaussian
from .Gaussian import LinearDiagionalGaussian

#from .FunctionLinearInFeatures import FunctionLinearInFeatures
#from .GaussianLinearInFeatures import GaussianLinearInFeatures


__all__ = ['DiagonalGaussian_Base',
           'ConstantDiagionalGaussian',
           'LinearDiagionalGaussian',
           'FeatureGenerator',
           'Function_Base',
           'LinearFunction',
           'Mapping'
           'TFMapping']

