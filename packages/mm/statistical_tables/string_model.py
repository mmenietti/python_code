#------------------------------------------------------------
# Dependencies
#------------------------------------------------------------
from collections import namedtuple
from dataclasses import dataclass, field
from typing      import Dict, Tuple, List

from object_model import RegressionTableFormatting, AdditionalFeatureParts, RegressionTableParts, CoefficientParts


#------------------------------------------------------------------------------    
#------------------------------------------------------------------------------    
#------------------------------------------------------------------------------    
CoefficientStrings = namedtuple(
    typename='CoefficientStrings', 
    field_names=['label','value','std_err','p_value','t_stat'],
    defaults=(None,None,None,None,None)
)

#------------------------------------------------------------------------------    
@dataclass
class RegressionStrings:
    coefficient_dict: Dict[str,CoefficientStrings] = field(default_factory=dict)
    additional_feature_dict: Dict[str,AdditionalFeatureParts] = field(default_factory=dict)
    label: str = None
    dependent_variable_label: str = None

#------------------------------------------------------------------------------    
@dataclass
class SxSRegressionStrings:
    regression_dict: Dict[str,RegressionStrings] = field(default_factory=dict)
    model_labels: Dict[str,str] = field(default_factory=dict)
    additional_feature_labels: Dict[str,str] = field(default_factory=dict)
    coefficient_labels: Dict[str,str] = field(default_factory=dict)
    notes: str = None

       
#------------------------------------------------------------
# 
#------------------------------------------------------------
def annotate_coefficient_significance(coefficient: float, p_value: float, string_format: str=':03.2f', significance_values: Tuple[float,float,float]=(0.10,0.05,0.01), significance_strings: Tuple[str,str,str]=('*','**','***')):
    string_interpolant = '{'+string_format+'}'

    if p_value > significance_values[0]:
        return string_interpolant.format(coefficient)
    elif p_value > significance_values[1]:
        return string_interpolant.format(coefficient)+significance_strings[0]
    elif p_value > significance_values[2]:
        return string_interpolant.format(coefficient)+significance_strings[1]
    elif p_value <= significance_values[2]:
        return string_interpolant.format(coefficient)+significance_strings[2]

#------------------------------------------------------------
# 
#------------------------------------------------------------
def coefficient_strings(coefficient: CoefficientParts, coefficient_label: str, formatting: RegressionTableFormatting):    
    
    value_string = annotate_coefficient_significance(
        coefficient=coefficient.value, 
        p_value=coefficient.p_value, 
        string_format=formatting.string_format,
        significance_values=formatting.significance_values,
        significance_strings=formatting.significance_strings
    )

    std_err_interpolant = formatting.std_err_bracket[0] + '{'+formatting.string_format+'}'+formatting.std_err_bracket[1]
    std_err_string = std_err_interpolant.format(coefficient.std_err)

    return CoefficientStrings(
        label = coefficient_label,
        value=value_string, 
        std_err=std_err_string, 
        p_value=('{'+formatting.string_format+'}').format(coefficient.p_value),
        t_stat=('{'+formatting.string_format+'}').format(coefficient.t_stat)
    )

#------------------------------------------------------------
# 
#------------------------------------------------------------
def regression_strings(regression: RegressionTableParts, model_label: str, dependent_variable_label: str, coefficient_labels: Dict[str,str], additional_feature_labels: Dict[str,str], formatting: RegressionTableFormatting):    
    regression_strings = RegressionStrings()

    regression_strings.label = model_label
    regression_strings.dependent_variable_label = dependent_variable_label

    for coefficient_name,coefficient_label in coefficient_labels.items():
        if coefficient_name in regression.coefficient_dict:
            coefficient = regression.coefficient_dict[coefficient_name]

            regression_strings.coefficient_dict[coefficient_name] = coefficient_strings(coefficient, coefficient_label, formatting)
        else:
            regression_strings.coefficient_dict[coefficient_name] = CoefficientStrings(
                label = coefficient_label,
                value='', 
                std_err='', 
                p_value='',
                t_stat=''
            )

    for feature_name in additional_feature_labels.keys():
        if feature_name in regression.additional_feature_dict:
            additional_feature = regression.additional_feature_dict[feature_name]            

            regression_strings.additional_feature_dict[feature_name] = additional_feature.value_interpolant.format(additional_feature.value)
        else:
            regression_strings.additional_feature_dict[feature_name] = ''    

    return regression_strings

#------------------------------------------------------------
# 
#------------------------------------------------------------
def create_sxs_regression_strings(regression_summary_dict: Dict[str,RegressionTableParts], model_labels: List[str], dependent_variable_labels: Dict[str,str],
                                     coefficient_labels: Dict[str,str], additional_feature_labels: Dict[str,str], notes: str, formatting: RegressionTableFormatting ):    
    
    # If no model labels given use index
    if model_labels is None:
        model_labels = {model_name : '({:d})'.format(idx+1) for idx,model_name in enumerate(regression_summary_dict.keys())}
        
    regression_dict = {}

    for regression_name,regression in regression_summary_dict.items():
        regression_dict[regression_name] = regression_strings(
            regression=regression, 
            model_label=model_labels[regression_name], 
            dependent_variable_label=dependent_variable_labels[regression.dependent_variable], 
            coefficient_labels=coefficient_labels, 
            additional_feature_labels=additional_feature_labels, 
            formatting=formatting
        )

    return SxSRegressionStrings(regression_dict, model_labels, additional_feature_labels, coefficient_labels, notes)

