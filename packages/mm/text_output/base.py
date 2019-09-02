import mm.text_output.markdown

from enum import Enum

#------------------------------------------------------------------------------    
# 
#------------------------------------------------------------------------------
class text_format(Enum):
    markdown = 1
    latex = 2
    plain = 3

format_file_extension_dict = {
    text_format.markdown : 'md',
    text_format.latex : 'tex',
    text_format.plain : 'txt'
}

#------------------------------------------------------------------------------    
# 
#------------------------------------------------------------------------------
def snake_case(*args):    
    in_str = [x.lower() for x in args]
    
    return "_".join(in_str)

#------------------------------------------------------------------------------    
# 
#------------------------------------------------------------------------------
def table_string(column_headers, column_values, table_format=text_format.markdown):
    
    if table_format == text_format.markdown:
        table_str = mm.text_output.markdown.table_string(column_headers, column_values)
    else:
        table_str = mm.text_output.markdown.table_string(column_headers, column_values)

    return table_str

#------------------------------------------------------------------------------    
# 
#------------------------------------------------------------------------------
def heading_string(level, heading_string, table_format=text_format.markdown):
    if table_format == text_format.markdown:
        heading_str = mm.text_output.markdown.heading_string(level, heading_string)
    else:
        heading_str = mm.text_output.markdown.heading_string(level, heading_string)

    return heading_str

#------------------------------------------------------------------------------    
# 
#------------------------------------------------------------------------------
def code_style(in_string, table_format=text_format.markdown):
    if table_format == text_format.markdown:
        code_style_str = mm.text_output.markdown.code_style(in_string)
    else:
        code_style_str = mm.text_output.markdown.code_style(in_string)

    return code_style_str
    