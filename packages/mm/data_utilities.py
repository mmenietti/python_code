import decimal
import math
import dateutil.parser
import itertools
import ast
import csv
import pyodbc

#------------------------------------------------------------------------------    
class ParsingError(Exception):
    # Exception raised for errors in the input.
    attempted_data_type = ''
    file_name = ''
    idx_col = 0
    idx_row = 0
    problem_value = None 

    def immediate_values(self, attempted_data_type, idx_col, idx_row, problem_value):
        self.attempted_data_type = attempted_data_type
        self.idx_col = idx_col
        self.idx_row = idx_row
        self.problem_value = problem_value

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return_string = ('Parse Error. '  
                        + ' File Name: ' + self.file_name
                        + ' Attempted Type: ' + self.attempted_data_type
                        + ' Problem Value: ' + self.problem_value
                        + ' Column: ' + str(self.idx_col)
                        + ' Row: ' + str(self.idx_row))
                            
        return return_string
        
#------------------------------------------------------------------------------    
def parse_table_data(column_values, idx_int=None, idx_float=None, idx_date=None, idx_decimal=None, idx_boolean=None, boolean_string_values=None ):
    
    # If no boolean strings given use the default text for printing booleans
    if (not boolean_string_values) and (idx_boolean):
        n_bools = len(idx_boolean)
        boolean_string_values = [('True', 'False')] * n_bools
    
    n_rows = len(column_values[0])
    
    for idx_row in range(n_rows):
        if idx_int:
            for idx in idx_int:
                try:
                    column_values[idx][idx_row] = try_int_parse(column_values[idx][idx_row])
                except ParsingError as parse_error:                    
                    parse_error.idx_col = idx
                    parse_error.idx_row = idx_row
                    raise parse_error
        if idx_float:
            for idx in idx_float:
                try:
                    column_values[idx][idx_row] = try_float_parse(column_values[idx][idx_row])
                except ParsingError as parse_error:                    
                    parse_error.idx_col = idx
                    parse_error.idx_row = idx_row
                    raise parse_error
        if idx_date:
            for idx in idx_date:
                try:
                    column_values[idx][idx_row] = try_date_parse(column_values[idx][idx_row])
                except ParsingError as parse_error:                    
                    parse_error.idx_col = idx
                    parse_error.idx_row = idx_row
                    raise parse_error
        if idx_decimal:
            for idx in idx_decimal:
                try:
                    column_values[idx][idx_row] = try_decimal_parse(column_values[idx][idx_row])
                except ParsingError as parse_error:                    
                    parse_error.idx_col = idx
                    parse_error.idx_row = idx_row
                    raise parse_error
        if idx_boolean:
            for k in range(len(idx_boolean)):
                idx = idx_boolean[k]
                truth_values = boolean_string_values[k]

                try:
                    column_values[idx][idx_row] = str_to_bool(column_values[idx][idx_row], truth_values[0], truth_values[1])
                except ParsingError as parse_error:                    
                    parse_error.idx_col = idx
                    parse_error.idx_row = idx_row
                    raise parse_error
        
    return column_values

#------------------------------------------------------------------------------  
def identify_type(input_data):
    try:
        return type(ast.literal_eval(input_data))
    except (ValueError, SyntaxError):
        # A string, so return str
        return str

#------------------------------------------------------------------------------  
def try_float_parse(s):
    try:
         return float(s)
    except ValueError: 
        return None
    
#------------------------------------------------------------------------------  
def try_decimal_parse(s):
    try:
         return decimal.Decimal(s)
    except decimal.InvalidOperation: 
        return None
    
#------------------------------------------------------------------------------  
def try_int_parse(s):
    try:
        s = float(s)
        if math.floor(s) == s:
            return int(s)
        else:
            return None
    except ValueError: 
        return None

#------------------------------------------------------------------------------  
def try_date_parse(s):
    try:
        s = dateutil.parser.parse(s, yearfirst=True)
        return s
    except ValueError: 
        return None

#------------------------------------------------------------------------------  
def sentinel_to_null(s, sentinel_value):
    if s == sentinel_value:
         return None
    else:
         return s

#------------------------------------------------------------------------------         
def str_to_bool(s, true_value, false_value):
    if s:
        if s == true_value:
            return True
        elif s == false_value:
            return False
        else:
            parse_error = ParsingError()
            parse_error.attempted_data_type='bool'
            parse_error.problem_value = s
            raise parse_error
    else:
        return None

#------------------------------------------------------------------------------    
def process_csv_data(csv_reader, has_headers=True):    
    if has_headers:
        column_headers = next(csv_reader)
        
        n_columns = len(column_headers)
        column_values = [[] for k in range(n_columns)] 
    else:
        column_headers = []
        first_row = next(csv_reader)
        n_columns = len(first_row)

        column_values = []
        for k in range(n_columns):
            column_values.append([first_row[k]])        

    for row in csv_reader:        
        for idx in range(len(row)):
            column_values[idx].append(row[idx])
                
    return (column_headers, column_values)

#------------------------------------------------------------------------------    
def check_column_names(canonical_headers, other_headers):    
    canonical_set = set(canonical_headers)
    other_set = set(other_headers)
    
    header_intersection = set.intersection(canonical_set, other_set)
    header_excluded = set.difference(canonical_set, other_set)
    header_included = set.difference(other_set, canonical_set)
        
    intersection_indices = [[canonical_headers.index(x) for x in header_intersection],
                            [other_headers.index(x) for x in header_intersection]]
    
    excluded_indices = [canonical_headers.index(x) for x in header_excluded]
    included_indices = [other_headers.index(x) for x in header_included]
                    
    return (header_intersection, header_excluded, header_included,
             intersection_indices, excluded_indices, included_indices)

#------------------------------------------------------------------------------    
def normalize_columns(canonical_headers, intersection_indices, excluded_indices, column_values):    
    normalized_column_values = [None] * len(canonical_headers)

    for idx0, idx1 in zip(intersection_indices[0], intersection_indices[1]):
        normalized_column_values[idx0] = column_values[idx1]

    for idx0 in excluded_indices:
        normalized_column_values[idx0] = itertools.repeat(None)
                    
    return normalized_column_values

#------------------------------------------------------------------------------    
def column_report(header_intersection, header_excluded, header_included, intersection_indices, excluded_indices, included_indices):
    header_intersection_report = 'Header Intersection: \n'
    header_excluded_report = 'Headers Excluded: \n'
    header_included_report = 'Headers Included: \n'

    if header_intersection:
        intersection_header_labels = [str(x) for x in header_intersection]
        intersection_header_indices = [str(x) for x in intersection_indices]

        intersection_header_labels = str.join(', ', intersection_header_labels)
        intersection_header_indices = str.join(', ', intersection_header_indices)
    else:
        intersection_header_labels = 'None'
        intersection_header_indices = 'None'

    if header_excluded:
        excluded_header_labels = [str(x) for x in header_excluded]
        excluded_header_indices = [str(x) for x in excluded_indices]

        excluded_header_labels = str.join(', ', excluded_header_labels)
        excluded_header_indices = str.join(', ', excluded_header_indices)
    else:
        excluded_header_labels = 'None'
        excluded_header_indices = 'None'
                    
    if header_included:
        included_header_labels = [str(x) for x in header_included]
        included_header_indices = [str(x) for x in included_indices]

        included_header_labels = str.join(', ', included_header_labels)
        included_header_indices = str.join(', ', included_header_indices)
    else:
        included_header_labels = 'None'
        included_header_indices = 'None'

    header_intersection_report = (header_intersection_report 
        + intersection_header_labels + '\n'
        + intersection_header_indices + '\n')

    header_excluded_report = (header_excluded_report 
        + excluded_header_labels + '\n'
        + excluded_header_indices + '\n')

    header_included_report = (header_included_report 
        + included_header_labels + '\n'
        + included_header_indices + '\n')

    return (header_intersection_report, header_excluded_report, header_included_report)             

#------------------------------------------------------------------------------    
# Helper function to parameterize the processing of  raw data files to clean output files.
#------------------------------------------------------------------------------ 
def process_data(input_file_path, output_file_path, data_processor, canonical_headers, preferred_headers):
    # Read data file
    with input_file_path.open('r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)    
        (headers, column_values) = process_csv_data(csv_reader)

    # Check File
    (_header_intersection, _header_excluded, _header_included,
     intersection_indices, excluded_indices, _included_indices)\
          = check_column_names(canonical_headers, headers)

    column_values = normalize_columns(
        canonical_headers, intersection_indices, excluded_indices, column_values)

    # Process values
    column_values = data_processor(column_values)

    # Write table to file
    if output_file_path.exists():
        # Write table to file, no header
        with output_file_path.open('a', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(zip(*column_values))
    else:
        # Write table to file, with header
        with output_file_path.open('w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(preferred_headers)
            writer.writerows(zip(*column_values))

#------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------    
# 
#------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------ 
if __name__ == '__main__':

    print('data_utilities')