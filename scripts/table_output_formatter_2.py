#------------------------------------------------------------
# Dependencies
#------------------------------------------------------------
import pathlib
import os
import argparse
import csv
import mm.data_utilities
import collections
import json

from dataclasses import dataclass, field
from typing import Tuple, Dict, List, Set

import docx
# from docx.shared import Inches

#------------------------------------------------------------------------------    
CoefficientParts = collections.namedtuple(
    typename='CoefficientParts', 
    field_names=['value','std_err','p_value','t_stat'],
    defaults=(None,None,None,None)
)

#------------------------------------------------------------------------------    
AdditionalFeatureParts = collections.namedtuple(
    typename='AdditionalFeatureParts', 
    field_names=['value','value_interpolant'],
    defaults=(None,None)
)

#------------------------------------------------------------------------------    
@dataclass
class RegressionTableParts:
    coefficient_dict: collections.OrderedDict()
    additional_feature_dict: collections.OrderedDict()
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
    regression_table_parts_dict: collections.OrderedDict()
    additional_features: Set[str] = field(default_factory=set)
    coefficients: Set[str] = field(default_factory=set)
    notes: str = None
    # formatting: RegressionTableFormatting = RegressionTableFormatting()

#------------------------------------------------------------------------------    
#------------------------------------------------------------------------------    
#------------------------------------------------------------------------------    
CoefficientStrings = collections.namedtuple(
    typename='CoefficientStrings', 
    field_names=['label','value','std_err','p_value','t_stat'],
    defaults=(None,None,None,None,None)
)

#------------------------------------------------------------------------------    
@dataclass
class RegressionStrings:
    coefficient_dict: collections.OrderedDict() = field(default_factory=dict)
    additional_feature_dict: collections.OrderedDict() = field(default_factory=dict)
    label: str = None
    dependent_variable_label: str = None

#------------------------------------------------------------------------------    
@dataclass
class SxSRegressionStrings:
    regression_dict: collections.OrderedDict()
    model_labels: Dict[str,str] = field(default_factory=dict)
    additional_feature_labels: Dict[str,str] = field(default_factory=dict)
    coefficient_labels: Dict[str,str] = field(default_factory=dict)
    notes: str = None

#------------------------------------------------------------
# File Contents Reader
#------------------------------------------------------------
def read_regression_table_json(json_path):
    with json_path.open() as file_handle:
        table_data = json.load(file_handle)

    coefficient_dict = collections.OrderedDict()

    coefficient_data = zip(table_data['coefficient_names'],
                           table_data['coefficient_values'],
                           table_data['coefficient_std_err'],
                           table_data['coefficient_t_value'],
                           table_data['coefficient_p_value'])
    
    for z in coefficient_data:
        coefficient_dict[z[0]] = CoefficientParts(
            value=mm.data_utilities.try_float_parse(z[1]),
            std_err=mm.data_utilities.try_float_parse(z[2]),
            p_value=mm.data_utilities.try_float_parse(z[3]),
            t_stat=mm.data_utilities.try_float_parse(z[4])
        )

    additional_feature_dict = collections.OrderedDict()
    additional_feature_dict['n'] = AdditionalFeatureParts(table_data['n_observations'], '{:d}')
    additional_feature_dict['r_sq'] = AdditionalFeatureParts(table_data['adj_r_squared'], '{:0.2f}') 

    return RegressionTableParts(
        dependent_variable = table_data['dependent_variable'],
        coefficient_dict = coefficient_dict,
        additional_feature_dict = additional_feature_dict
    )

def read_regression_table_data(csv_reader):
    (_column_headers, column_values) = mm.data_utilities.process_csv_data(csv_reader, has_headers=True)

    coefficient_dict = collections.OrderedDict()
    for z in zip(*column_values):
        coefficient_dict[z[1]] = CoefficientParts(
            value=mm.data_utilities.try_float_parse(z[2]),
            std_err=mm.data_utilities.try_float_parse(z[3]),
            p_value=mm.data_utilities.try_float_parse(z[4]),
            t_stat=mm.data_utilities.try_float_parse(z[5])
        )

    return RegressionTableParts(
        dependent_variable = 'dependent_variable',
        coefficient_dict = coefficient_dict,
        additional_feature_dict = collections.OrderedDict()
    )
       
#------------------------------------------------------------
# 
#------------------------------------------------------------
def annotate_coefficient_significance(coefficient, p_value, string_format=':03.2f', significance_values=(0.10,0.05,0.01), significance_strings=('*','**','***')):
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
def coefficient_strings(coefficient, coefficient_label, formatting: RegressionTableFormatting):    
    
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
def regression_strings(regression, model_label, dependent_variable_label, coefficient_labels, additional_feature_labels, formatting: RegressionTableFormatting):    
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
def sxs_regression_strings(sxs_regressions, model_labels, dependent_variable_labels, coefficient_labels, additional_feature_labels, notes, formatting: RegressionTableFormatting ):    
    
    # If no model labels given use index
    if model_labels is None:
        model_labels = {model_name : '({:d})'.format(idx+1) for idx,model_name in enumerate(sxs_regressions.regression_table_parts_dict.keys())}
        
    regression_dict = collections.OrderedDict()

    for regression_name,regression in sxs_regressions.regression_table_parts_dict.items():
        regression_dict[regression_name] = regression_strings(
            regression=regression, 
            model_label=model_labels[regression_name], 
            dependent_variable_label=dependent_variable_labels[regression.dependent_variable], 
            coefficient_labels=coefficient_labels, 
            additional_feature_labels=additional_feature_labels, 
            formatting=formatting
        )

    return SxSRegressionStrings(regression_dict, model_labels, additional_feature_labels, coefficient_labels, notes)

#------------------------------------------------------------------------------    
#------------------------------------------------------------------------------    
#------------------------------------------------------------------------------    
def label_column_str_list(coefficient_labels, additional_feature_labels):    

    column_strings = []    
    
    # Coefficients
    for label in coefficient_labels.values():
        column_strings.append(label)
        column_strings.append('')

    # Additional Features
    for label in additional_feature_labels.values():
        column_strings.append(label)

    return column_strings

def regression_column_str_list(regression_label, regression: RegressionStrings, coefficient_labels, additional_feature_labels):    

    column_strings = []

    # Label
    column_strings.append(regression_label)
    
    # Coefficients and Std. Errors
    for coefficient_ in coefficient_labels.keys():
        coefficient = regression.coefficient_dict[coefficient_]

        column_strings.append(coefficient.value)
        column_strings.append(coefficient.std_err)

    # Additional Features
    for feature_name in additional_feature_labels.keys():
        column_strings.append(regression.additional_feature_dict[feature_name])

    return column_strings

def sxs_regression_table_docx(sxs_regressions: SxSRegressionStrings, document: docx.Document):    
    
    n_regressions = len(sxs_regressions.regression_dict)
    n_coefficients = len(sxs_regressions.coefficient_labels)
    n_additional_features = len(sxs_regressions.additional_feature_labels)

    # Rows for coefficient values and Std. Errors,
    # additional features, model labels, and notes
    n_rows = 2*n_coefficients + n_additional_features + 2
    
    # Columns for Models and labels
    n_cols = n_regressions + 1 
    
    table = document.add_table(n_rows, n_cols)

    # Coefficient and Additional Feature Labels
    column_cells = table.column_cells(0)
    column_strings = label_column_str_list(sxs_regressions.coefficient_labels, sxs_regressions.additional_feature_labels)
    
    for idx, string_value in enumerate(column_strings):
        column_cells[1+idx].text = string_value

    # Model Columns
    for reg_idx, (reg_name, reg_label) in enumerate(sxs_regressions.model_labels.items()):
        regression = sxs_regressions.regression_dict[reg_name]

        # Coefficients, Std. Errors, and Additional Features
        column_strings = regression_column_str_list(reg_label, regression, sxs_regressions.coefficient_labels, sxs_regressions.additional_feature_labels)

        column_cells = table.column_cells(1+reg_idx)
        for idx, string_value in enumerate(column_strings):
            column_cells[idx].text = string_value

    # Notes
    row_cells = table.row_cells(n_rows-1)
    row_cells[0].text = 'Note:'
    notes_cell = row_cells[1].merge(row_cells[n_cols-1])
    notes_cell.text = sxs_regressions.notes




    # # Coefficient and Additional Feature Value Labels
    # column_cells = table.column_cells(0)
    # for idx, label in enumerate(sxs_regressions.coefficient_labels.values()):
    #     column_cells[1 + 2*idx].text = label    

    # for idx, label in enumerate(sxs_regressions.additional_feature_labels.values()):
    #     column_cells[1 + 2*n_coefficients + idx].text = label    


    # # Model Coefficients and Additional Feature Values
    # for reg_idx, regression in enumerate(sxs_regressions.regression_dict.values()):
    #     column_cells = table.column_cells(1+reg_idx)
    #     for coeff_idx,coefficient in enumerate(regression.coefficient_dict.values()):
    #         column_cells[1+2*coeff_idx].text = coefficient.value
    #         column_cells[2+2*coeff_idx].text = coefficient.std_err

    return document




#------------------------------------------------------------
# Entry Point
#------------------------------------------------------------
if __name__ == "__main__":
    # # Parse Command-line Arguments
    # parser = argparse.ArgumentParser(description='Process path string.')
    # parser.add_argument('inserts_directory')
    # parser.add_argument('input_file')
    # parser.add_argument('output_file')
    
    # args = parser.parse_args()    
    
    # Setup file paths to inputs and outputs
    input_file_path        = pathlib.Path('./test_table_1.json')  
    # output_file_path       = pathlib.Path(args.output_file)  

    regression_table_parts_1 = read_regression_table_json(pathlib.Path('./views_on_partition_table_1_1.json'))
    regression_table_parts_2 = read_regression_table_json(pathlib.Path('./views_on_partition_table_1_2.json'))
    regression_table_parts_3 = read_regression_table_json(pathlib.Path('./views_on_partition_table_1_3.json'))
    regression_table_parts_4 = read_regression_table_json(pathlib.Path('./views_on_partition_table_1_4.json'))
        
    # annotated_coefficients = annotate_significance(regression_table_parts.coefficient, regression_table_parts.p_value)
    # coefficient_table_str = coefficient_table_string(regression_table_parts.coefficient, regression_table_parts.std_err, regression_table_parts.p_value)

    # regression_table_parts.additional_feature_dict = {'n' : AdditionalFeatureParts(100,'{:d}'),'r_sq':AdditionalFeatureParts(2.0/3.0,'{:1.2f}')}

    regression_table_parts_dict = collections.OrderedDict()
    regression_table_parts_dict['model_1'] = regression_table_parts_1
    regression_table_parts_dict['model_2'] = regression_table_parts_2
    regression_table_parts_dict['model_3'] = regression_table_parts_3
    regression_table_parts_dict['model_4'] = regression_table_parts_4

    # regression_table_parts_dict['model_1'].dependent_variable = 'a_outcome'
    # regression_table_parts_dict['model_2'].dependent_variable = 'b_outcome'
    # regression_table_parts_dict['model_3'].dependent_variable = 'c_outcome'

    coefficient_names = ["(Intercept)","migratedTRUE","migrated_to_pakistanTRUE"]

    sxs_regression_table_parts = SxSRegressionTableParts(
        regression_table_parts_dict=regression_table_parts_dict,
        additional_features= {},
        coefficients=coefficient_names,
        notes = None
        # formatting=formatting
    )

    coefficient_labels = {
        "(Intercept)":'Constant',
        'migratedTRUE':'Migrated',
        'migrated_to_pakistanTRUE':'to Pakistan'
    }

    dependent_variable_labels = {
        'non_negative_view_on_partition':'non_negative_view_on_partition'
    }

    notes = 'This is a note'
    formatting = RegressionTableFormatting()

    sxs_strings = sxs_regression_strings(
        sxs_regressions=sxs_regression_table_parts, 
        model_labels=None,
        dependent_variable_labels = dependent_variable_labels,
        coefficient_labels=coefficient_labels, 
        additional_feature_labels={'n':'N', 'r_sq':'Adj. R Sq.'}, 
        notes=notes,
        formatting=formatting        
    )
    
    document = docx.Document('blank_document_o365_2020_04_28.docx')    
    document = sxs_regression_table_docx(sxs_strings, document)
    document.save('test.docx')
