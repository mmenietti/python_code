#------------------------------------------------------------
# Dependencies
#------------------------------------------------------------
from collections import namedtuple
from dataclasses import dataclass, field
from typing      import Tuple, Set, Dict

#------------------------------------------------------------------------------    
CoefficientParts = namedtuple(
    typename='CoefficientParts', 
    field_names=['value','std_err','p_value','t_stat'],
    defaults=(None,None,None,None)
)

#------------------------------------------------------------------------------    
AdditionalFeatureParts = namedtuple(
    typename='AdditionalFeatureParts', 
    field_names=['value','value_interpolant'],
    defaults=(None,None)
)

#------------------------------------------------------------------------------    
@dataclass
class RegressionTableParts:
    coefficient_dict: dict
    additional_feature_dict: dict
    dependent_variable: str = None

#------------------------------------------------------------------------------    
@dataclass
class RegressionTableFormatting:
    string_format: str = ':03.2f'
    significance_values: Tuple[float,float,float] = (0.10,0.05,0.01)
    significance_strings: Tuple[str,str,str] = ('*','**','***')
    std_err_bracket: str = '()'

#------------------------------------------------------------------------------    
@dataclass
class SxSRegressionTableParts:
    regression_table_parts_dict: dict
    additional_features: Set[str] = field(default_factory=set)
    coefficients: Set[str] = field(default_factory=set)
    notes: str = None
