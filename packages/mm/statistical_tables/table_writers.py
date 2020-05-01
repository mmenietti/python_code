#------------------------------------------------------------
# Dependencies
#------------------------------------------------------------

# Standard
from dataclasses import dataclass, field
from typing      import Tuple
# Third Party
from docx import Document

# Intra package
from string_model import SxSRegressionStrings, RegressionStrings

#------------------------------------------------------------
# Classes
#------------------------------------------------------------
@dataclass
class DocxRegressionTableFormatting:
    string_format: str = ':03.2f'
    significance_values: Tuple[float,float,float] = (0.10,0.05,0.01)
    significance_strings: Tuple[str,str,str] = ('*','⋆⋆','***')
    std_err_bracket: str = '()'

#------------------------------------------------------------
# Functions
#------------------------------------------------------------
def write_sxs_regression_table_docx(sxs_regressions: SxSRegressionStrings, document: Document):    
    
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

    return document

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