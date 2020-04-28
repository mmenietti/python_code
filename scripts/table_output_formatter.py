#------------------------------------------------------------
# Dependencies
#------------------------------------------------------------
import pathlib
import os
import argparse
import csv
import mm.data_utilities
import collections

#------------------------------------------------------------------------------    
RegressionTableParts = collections.namedtuple(typename='RegressionTableParts', 
                                              field_names=['coefficient_label', 'coefficient_name','coefficient', 'std_err', 'p_value', 't_stat', 'model_label', 'dependent_variable'],
                                              defaults=(None,None,None,None,None,None,None,None))

#------------------------------------------------------------------------------    
RegressionTableFormatting = collections.namedtuple(typename='RegressionTableFormatting', 
                                              field_names=['string_format', 'significance_values', 'significance_strings','std_err_bracket'],
                                              defaults=(':03.2f',(0.10,0.05,0.01),('*','**','***'),'()'))

#------------------------------------------------------------
# File Contents Reader
#------------------------------------------------------------
def read_regression_table_data(csv_reader):
    (_column_headers, column_values) = mm.data_utilities.process_csv_data(csv.reader(in_file), has_headers=True)

    return RegressionTableParts(coefficient_label = column_values[0],
                                coefficient_name = column_values[1],
                                coefficient = [mm.data_utilities.try_float_parse(x) for x in column_values[2]],
                                std_err = [mm.data_utilities.try_float_parse(x) for x in column_values[3]],
                                p_value = [mm.data_utilities.try_float_parse(x) for x in column_values[4]],
                                t_stat = [mm.data_utilities.try_float_parse(x) for x in column_values[5]])

#------------------------------------------------------------
# 
#------------------------------------------------------------
def annotate_significance(coefficient, p_value, string_format=':03.2f', significance_values=(0.10,0.05,0.01), significance_strings=('*','**','***')):
    
    string_interpolant = '{'+string_format+'}'

    def annotate(coefficient_and_p_value):
        coefficient = coefficient_and_p_value[0]
        p_value = coefficient_and_p_value[1]

        if p_value > significance_values[0]:
            return string_interpolant.format(coefficient)
        elif p_value > significance_values[1]:
            return string_interpolant.format(coefficient)+significance_strings[0]
        elif p_value > significance_values[2]:
            return string_interpolant.format(coefficient)+significance_strings[1]
        elif p_value <= significance_values[2]:
            return string_interpolant.format(coefficient)+significance_strings[2]

    return [annotate(z) for z in zip(coefficient,p_value)]
        
#------------------------------------------------------------
# 
#------------------------------------------------------------
def coefficient_table(coefficient, std_err, p_value, string_format=':03.2f', significance_values=(0.10,0.05,0.01), significance_strings=('*','**','***'),std_err_bracket='()'):
    std_err_interpolant = std_err_bracket[0] + '{'+string_format+'}'+std_err_bracket[1]

    annotated_coefficients = annotate_significance(coefficient, p_value)
    bracketed_std_err = [std_err_interpolant.format(z) for z in std_err]

    n_coefficients = len(coefficient)

    coefficient_table_str = [[] for z in range(2*n_coefficients)]
    coefficient_table_str[::2] = annotated_coefficients
    coefficient_table_str[1::2] = bracketed_std_err

    return coefficient_table_str







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
    input_file_path        = pathlib.Path('./test_table.txt')  
    # output_file_path       = pathlib.Path(args.output_file)  

    with input_file_path.open(mode='r', newline='') as in_file:
        csv_reader = csv.reader(in_file)        
        regression_table_parts = read_regression_table_data(csv_reader)
    
    annotated_coefficients = annotate_significance(regression_table_parts.coefficient, regression_table_parts.p_value)

    coefficient_table_str = coefficient_table(regression_table_parts.coefficient, regression_table_parts.std_err, regression_table_parts.p_value)
    print(coefficient_table_str)