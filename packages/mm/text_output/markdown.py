#------------------------------------------------------------------------------    
# 
#------------------------------------------------------------------------------
def table_string(column_headers, column_values):
    """Formats given table data as a markdown pipe_tables table."""
    #  Constants for markdown formatting
    col_delimiter = '|'
    row_delimiter = '\n'
    rule_str = '-'
    md_alignment_str = ':'

    n_col = len(column_headers)
    
    # Convert values to strings
    column_value_str = []

    for k in range(n_col):
        column_value_str.append([str(z) for z in column_values[k]])

    # Find max width in each column
    col_widths = []
    
    for k, x in enumerate(column_value_str):        
        value_width = len(max(x, key=len))
        header_width = len(column_headers[k])
        
        col_widths.append(max((value_width, header_width)))

    # Create rule for the top and bottom
    # rule = [rule_str * (w+2) for w in col_widths]
    # rule = col_delimiter + col_delimiter.join(rule) + col_delimiter + row_delimiter

    # Create rule for below header
    header_rule = [rule_str * (w+1) for w in col_widths]
    header_rule = col_delimiter + md_alignment_str + (col_delimiter + md_alignment_str).join(header_rule) + col_delimiter + row_delimiter

    # Create format string for table rows
    pos_argument = lambda k, w: ' {' + str(k) +  ':<' + str(w) + '} '
    positional_arguments = [ pos_argument(k, col_widths[k])  for k in range(n_col)]
    
    row_format_str = col_delimiter + col_delimiter.join(positional_arguments) + col_delimiter + row_delimiter

    # Build table string
    table_str = row_format_str.format(*column_headers) + header_rule

    for row in zip(*column_value_str):
        table_str += row_format_str.format(*row)

    return (table_str)

#------------------------------------------------------------------------------    
# 
#------------------------------------------------------------------------------
def heading_string(level, heading_string):
    
    return ('#' * level) + ' ' + heading_string

#------------------------------------------------------------------------------    
# 
#------------------------------------------------------------------------------
def code_style(in_string):    
    return '`' + in_string + '`'

#------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------    
# 
#------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------ 
if __name__ == '__main__':

    print('mm.text_output.markdown')
