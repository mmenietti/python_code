#------------------------------------------------------------
# Dependencies
#------------------------------------------------------------
from pathlib     import Path
from collections import OrderedDict
from json        import load

from mm.data_utilities import try_float_parse

from object_model import AdditionalFeatureParts, CoefficientParts, RegressionTableParts


#------------------------------------------------------------
# File Contents Reader
#------------------------------------------------------------
def read_regression_table_json(json_path: Path):
    with json_path.open() as file_handle:
        table_data = load(file_handle)

    coefficient_dict = OrderedDict()

    coefficient_data = zip(table_data['coefficient_names'],
                           table_data['coefficient_values'],
                           table_data['coefficient_std_err'],
                           table_data['coefficient_t_value'],
                           table_data['coefficient_p_value'])
    
    for z in coefficient_data:
        coefficient_dict[z[0]] = CoefficientParts(
            value=try_float_parse(z[1]),
            std_err=try_float_parse(z[2]),
            t_stat=try_float_parse(z[3]),
            p_value=try_float_parse(z[4])
        )

    additional_feature_dict = OrderedDict()
    additional_feature_dict['n'] = AdditionalFeatureParts(table_data['n_observations'], '{:d}')
    additional_feature_dict['r_sq'] = AdditionalFeatureParts(table_data['adj_r_squared'], '{:0.2f}') 

    return RegressionTableParts(
        dependent_variable = table_data['dependent_variable'],
        coefficient_dict = coefficient_dict,
        additional_feature_dict = additional_feature_dict
    )
