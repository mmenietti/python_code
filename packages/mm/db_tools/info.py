import typing
import pathlib
import pyodbc
import csv

import mm.text_output.base

import metadata

#------------------------------------------------------------------------------
# Classes
#------------------------------------------------------------------------------
class table_summation(typing.NamedTuple):
    table_type     : str
    column_summary : str

#------------------------------------------------------------------------------
class schema_report(typing.NamedTuple):
    table_descriptor_dict    : dict
    interpolation_field_dict : dict    
    template                 : str

#------------------------------------------------------------------------------
class database_report(typing.NamedTuple):
    schema_summary_dict      : dict
    interpolation_field_dict : dict    
    template                 : str

#------------------------------------------------------------------------------
# Summary Table Functions
#------------------------------------------------------------------------------
def build_table_summary(column_descriptor_dict, variable_description_dict={}, table_format=mm.text_output.base.text_format.markdown):    

    # Parameters for empty variable descriptions
    placeholder_length = 50
    placeholder_str = " " * placeholder_length

    #  Fill missing variable descriptions with placeholder text.
    incomplete_column_description_set = column_descriptor_dict.keys() - variable_description_dict.keys()

    for x in incomplete_column_description_set:
        variable_description_dict[x] = placeholder_str

    # Fill out column values.
    # Wrap the variable names and types in backticks so they are typeset as code in markdown.
    column_headers = ['Variable', 'Type', 'Nullable', 'Description']

    column_name = []
    column_type = []
    column_nullable = []
    column_description = []
    for i_column_name, i_column_descriptor in column_descriptor_dict.items():
        column_name.append(mm.text_output.base.code_style(i_column_name.strip(), table_format))
        column_type.append(mm.text_output.base.code_style(i_column_descriptor.database_type.strip(), table_format))
        column_nullable.append(i_column_descriptor.nullable_bool)
        column_description.append(variable_description_dict[i_column_name])

    column_values = [column_name, column_type, column_nullable, column_description]

    return mm.text_output.base.table_string(column_headers, column_values, table_format)

#------------------------------------------------------------------------------
def build_schema_table_summary(table_descriptor_dict={}, variable_description_dict={}, table_format=mm.text_output.base.text_format.markdown):    
    
    schema_summary_dict = {}

    for i_table_name, i_table_descriptor in table_descriptor_dict.items():
        schema_summary_dict[i_table_name] = table_summation(i_table_descriptor.table_type, build_table_summary(i_table_descriptor.column_descriptor_dict, variable_description_dict, table_format))

    return schema_summary_dict
 
#------------------------------------------------------------------------------
def build_database_schema_table_summary(schema_descriptor_dict={}, variable_description_dict={}, table_format=mm.text_output.base.text_format.markdown):
    
    database_summary_dict = {}

    for schema_name, table_descriptor_dict in schema_descriptor_dict.items():
        database_summary_dict[schema_name] = build_schema_table_summary(table_descriptor_dict, variable_description_dict, table_format)

    return database_summary_dict

#------------------------------------------------------------------------------
# Interpolation field Functions
#------------------------------------------------------------------------------
def build_table_interpolation_field(table_name, schema_name, database_name):
    return '{' + database_name + '_' + schema_name + '_' + table_name + '}'

#------------------------------------------------------------------------------
def build_schema_interpolation_field(table_descriptor_dict, schema_name, database_name):

    schema_interpolation_field_dict = {}

    for table_name in table_descriptor_dict.keys():
        schema_interpolation_field_dict[table_name] = build_table_interpolation_field(table_name, schema_name, database_name)

    return schema_interpolation_field_dict

#------------------------------------------------------------------------------
def build_database_interpolation_field(schema_descriptor_dict, database_name):

    database_interpolation_field_dict = {}

    for schema_name, i_table_descriptor_dict in schema_descriptor_dict.items():
        database_interpolation_field_dict[schema_name] = build_schema_interpolation_field(i_table_descriptor_dict, schema_name, database_name)

    return database_interpolation_field_dict

#------------------------------------------------------------------------------
# Report Functions
#------------------------------------------------------------------------------
def build_schema_report(table_descriptor_dict, schema_name, database_name,
                       variable_description_dict={},
                       table_format=mm.text_output.base.text_format.markdown,
                       heading_level=1):

    schema_summary_dict = build_schema_table_summary(table_descriptor_dict, variable_description_dict, table_format)
    table_interpolation_field_dict = build_schema_interpolation_field(schema_summary_dict, schema_name, database_name)

    table_interpolation_field_flat_dict = {}
    template = mm.text_output.base.heading_string(heading_level, schema_name) + '\n\n'

    for i_table_name, i_field in table_interpolation_field_dict.items():
        field_label = database_name + '_' + schema_name + '_' + i_table_name
        table_interpolation_field_flat_dict[field_label] = schema_summary_dict[i_table_name].column_summary

        template += mm.text_output.base.heading_string(heading_level+1,
                                                       mm.text_output.base.code_style(i_table_name, table_format) + ', '
                                                        + mm.text_output.base.code_style(schema_summary_dict[i_table_name].table_type, table_format) ) + '\n\n'
        template += i_field + '\n\n'

    return schema_report(schema_summary_dict, table_interpolation_field_flat_dict, template)

#------------------------------------------------------------------------------
def build_database_report(schema_descriptor_dict, database_name,
                       variable_description_dict={},
                       table_format=mm.text_output.base.text_format.markdown,
                       heading_level=1):

    database_summary_dict = {}
    schema_interpolation_field_dict = {}
    template = mm.text_output.base.heading_string(heading_level, database_name) + '\n\n'

    for i_schema_name, i_table_descriptor_dict in schema_descriptor_dict.items():
        (database_summary_dict[i_schema_name], i_interpolation_field_dict, schema_template)\
             = build_schema_report(i_table_descriptor_dict, i_schema_name, database_name, variable_description_dict, table_format, heading_level + 1)
        
        template += schema_template
        schema_interpolation_field_dict.update(i_interpolation_field_dict)


    return database_report(database_summary_dict, schema_interpolation_field_dict, template)

#------------------------------------------------------------------------------
# Convenience Functions
#------------------------------------------------------------------------------
def build_inline_report(in_report):
    return in_report[2].format(**in_report[1])

#------------------------------------------------------------------------------
def write_interpolated_report(in_report, template_path, table_summary_path, table_format=mm.text_output.base.text_format.markdown):
    
    template_path.write_text(in_report[2], encoding='utf-8')

    file_extension = mm.text_output.base.format_file_extension_dict[table_format]

    if table_summary_path.is_dir():
        for i_field_name, i_summary in in_report[1].items():
            outfile_path = table_summary_path.joinpath(i_field_name + '.' + file_extension)
            outfile_path.write_text(i_summary, encoding='utf-8')

#------------------------------------------------------------------------------    
# Variable Description Functions
#------------------------------------------------------------------------------
def read_variable_description_file(input_file_path):    

    with input_file_path.open('r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        (_col_headers, column_values) = mm.data_utilities.process_csv_data(csv_reader, has_headers=False)

    variable_descriptions = dict(zip(*column_values))
    return variable_descriptions

#------------------------------------------------------------------------------    
# 
#------------------------------------------------------------------------------
def write_variable_description_template_file(output_file_path, variable_names, variable_descriptions=dict()):    

    for var in variable_names:
        if var not in variable_descriptions:
            variable_descriptions[var] = ''

    with output_file_path.open('w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(zip(variable_descriptions.keys(), variable_descriptions.values()))    

#------------------------------------------------------------------------------ 
# Entry Point
#------------------------------------------------------------------------------ 
if __name__ == '__main__':

    db_name = 'srm_badges'
    db_connection = lambda : pyodbc.connect("DSN=ResearchData; Trusted_Connection=yes;")    

    db_schema = 'analysis'
    db_table = 'cross_section'
    db_schema_list = ['analysis', 'processed', 'data_definitions']   

    template_root_path = pathlib.Path('C:/Users/micha/OneDrive - Harvard Business School/python') 
    summary_root_path = pathlib.Path('C:/Users/micha/OneDrive - Harvard Business School/python/tables') 

    #------------------------------------------------------------------------------        
    table_metadata    = metadata.fetch_table(db_connection, db_name, db_schema, db_table)
    schema_metadata   = metadata.fetch_schema_table(db_connection, db_name, db_schema)
    database_metadata = metadata.fetch_database_schema_table(db_connection, db_name, db_schema_list)

    table_summation_str     = build_table_summary(table_metadata)
    schema_summation_dict   = build_schema_table_summary(schema_metadata)
    database_summation_dict = build_database_schema_table_summary(database_metadata)
    
    table_interpolation_field_str = build_table_interpolation_field(db_table, db_schema, db_name)
    schema_interpolation_dict     = build_schema_interpolation_field(schema_summation_dict, db_schema, db_name) 
    database_interpolation_dict   = build_database_interpolation_field(database_summation_dict, db_name)

    schema_report_struct   = build_schema_report(schema_metadata, db_schema, db_name)
    database_report_struct = build_database_report(database_metadata, db_name)

    schema_inline_report = build_inline_report(schema_report_struct)
    database_inline_report = build_inline_report(database_report_struct)

    # #------------------------------------------------------------------------------ 
    # print(table_summation_str)
    # 
    # for i_table_name, i_table_summation in schema_summation_dict.items():
    #     print(i_table_name + ' ' + i_table_summation.table_type + '\n\n')
    #     print(i_table_summation.column_summary)    
    # 
    # for i_schema_name, i_schema_summation in database_summation_dict.items():
    #     print(i_schema_name + '\n\n')
    #     for i_table_name, i_table_summation in i_schema_summation.items():
    #         print(i_table_name + ' ' + i_table_summation.table_type + '\n\n')
    #         print(i_table_summation.column_summary)
    # 
    # #------------------------------------------------------------------------------
    # print(table_interpolation_field_str)
    # 
    # for table_name, i_table_summary_str in schema_interpolation_dict.items():
    #     print(table_name + '\n')
    #     print(i_table_summary_str)  
    # 
    # for schema_name, i_schema_interpolation_dict in database_interpolation_dict.items():
    #     print(schema_name + '\n\n')
    #     for table_name, i_table_interpolation_field_str in i_schema_interpolation_dict.items():
    #         print(table_name + '\n')
    #         print(i_table_interpolation_field_str)
    # 
    # #------------------------------------------------------------------------------
    # print(schema_report_struct.interpolation_field_dict)
    # print(schema_report_struct.template) 
    # 
    # print(database_report_struct.interpolation_field_dict)
    # print(database_report_struct.template)
    # 
    # print(schema_report_struct.template.format(**schema_report_struct.interpolation_field_dict))
    # print(database_report_struct.template.format(**database_report_struct.interpolation_field_dict))
    #    
    # #------------------------------------------------------------------------------
    # print(schema_inline_report)
    # print(database_inline_report)
    # 
    # #------------------------------------------------------------------------------
    # write_interpolated_report(schema_report_struct, template_root_path.joinpath('schema_report.md'), summary_root_path)
    # write_interpolated_report(database_report_struct, template_root_path.joinpath('database_report.md'), summary_root_path)