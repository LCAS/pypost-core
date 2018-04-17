from .Mapping import Mapping
from .TFMapping import TFMapping
from .Function import Function_Base
from .Function import LinearFunction
from .Function import ConstantFunction
from .Function import MLPFunction
from .Gaussian import DiagonalGaussian_Base
from .Gaussian import ConstantDiagonalGaussian
from .Gaussian import LinearDiagonalGaussian
from .Gaussian import FullGaussian_Base
from .Gaussian import LinearFullGaussian
from .Gaussian import FullGaussian
from .Gaussian import MLPFullGaussian

from .DataManipulator import CallType, DataManipulator, additional_inputs

#from .FunctionLinearInFeatures import FunctionLinearInFeatures
#from .GaussianLinearInFeatures import GaussianLinearInFeatures


__all__ = ['DiagonalGaussian_Base',
           'ConstantDiagonalGaussian',
           'LinearDiagonalGaussian',
           'Function_Base',
           'LinearFunction',
           'Mapping'
           'TFMapping']

