import csv
import mm.data_utilities

#------------------------------------------------------------------------------    
def insert_into_db(column_data, column_names, db_cursor, db_table_name, db_schema_name, db_name):
    """Insert 'column_data' into database table."""

    insert_data = zip(*column_data)
    n_columns = len(column_data)

    db_path =  db_name + '.' + db_schema_name + '.' + db_table_name

    sql_commands = 'insert into ' + db_path
    sql_variables = '(' + ','.join(column_names) + ')'
    sql_parameters = 'Values(' + '?,'*(n_columns-1) + '?)'

    sql_full_command = sql_commands + sql_variables + sql_parameters
    print(sql_full_command)
    db_cursor.executemany(sql_full_command, insert_data)
    db_cursor.commit()

#------------------------------------------------------------------------------    
def insert_tuples_into_db(tuple_data, column_names, db_cursor, db_table_name, db_schema_name, db_name):
    """Insert 'tuple_data' into database table."""
    n_columns = len(tuple_data[0])

    db_path =  db_name + '.' + db_schema_name + '.' + db_table_name

    sql_commands = 'insert into ' + db_path
    sql_variables = '(' + ','.join(column_names) + ')'
    sql_parameters = 'Values(' + '?,'*(n_columns-1) + '?)'

    sql_full_command = sql_commands + sql_variables + sql_parameters
    
    db_cursor.executemany(sql_full_command, tuple_data)
    db_cursor.commit()

#------------------------------------------------------------------------------    
def insert_csv_into_db(data_file_path, db_table_name, db_schema_name, db_name, db_connection, column_names, data_processor):
    """Insert the 'data_file_path' (a csv file) database table."""
    with data_file_path.open('r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)    
        (_column_headers, column_values) = mm.data_utilities.process_csv_data(csv_reader)

        try:
            column_values = data_processor(column_values)
        except mm.data_utilities.ParsingError as parse_error:
            parse_error.file_name = data_file_path.name            
            print(parse_error)

    # Database Connection and Cursor
    with db_connection()  as cnxn:
        db_cursor = cnxn.cursor()
        insert_into_db(column_values, column_names, db_cursor, db_table_name, db_schema_name, db_name)

#------------------------------------------------------------------------------ 
def write_db_data_2_file(output_file_path, db_connection, db_name, db_schema, db_table):

    db_path =  db_name + '.' + db_schema + '.' + db_table
    sql_command = 'select * from ' + db_path

    # Database Connection and Cursor
    with db_connection()  as cnxn:
        db_cursor = cnxn.cursor()
        column_names = [z[3] for z in db_cursor.columns(table=db_table, catalog=db_name, schema=db_schema)]
        rows = db_cursor.execute(sql_command).fetchall()
    
    # Write table to file, with header
    with output_file_path.open('w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(column_names)
        writer.writerows(rows)

#------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------    
# 
#------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------ 
if __name__ == '__main__':

    print('mm.data_utilities')