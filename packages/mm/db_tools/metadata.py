import pyodbc
import typing

class column_descriptor(typing.NamedTuple):
    database_type: str
    size         : int
    nullable_bool: bool

class table_descriptor(typing.NamedTuple):
    table_type : str
    column_descriptor_dict : dict 

#------------------------------------------------------------------------------    
#  0: table_cat
#  1: table_schem
#  2: table_name
#  3: column_name
#  4: data_type
#  5: type_name
#  6: column_size
#  7: buffer_length
#  8: decimal_digits
#  9: num_prec_radix
# 10: nullable
# 11: remarks
# 12: column_def
# 13: sql_data_type
# 14: sql_datetime_sub
# 15: char_octet_length
# 16: ordinal_position
# 17: is_nullable: One of SQL_NULLABLE, SQL_NO_NULLS, SQL_NULLS_UNKNOWN.

def fetch_table(db_connection, db_name, db_schema, db_table):
    """Fetches table metadata from database. Returns dict of column descriptors."""
    with db_connection() as cnxn:
        db_cursor = cnxn.cursor()
        column_descriptor_list = [z for z in db_cursor.columns(catalog=db_name, schema=db_schema, table=db_table)]
    
    column_descriptor_dict = {}

    for descriptor in column_descriptor_list:        
        column_name   = descriptor[3]

        column_descriptor_dict[column_name] = column_descriptor(
            database_type = descriptor[5], 
            size          = descriptor[6],
            nullable_bool = descriptor[10] > 0
        )

    return column_descriptor_dict

#------------------------------------------------------------------------------    
# 
#------------------------------------------------------------------------------
# 0: table_cat: The catalog name.
# 1: table_schem: The schema name.
# 2: table_name: The table name.
# 3: table_type: One of the string values 'TABLE', 'VIEW', 'SYSTEM TABLE', 'GLOBAL TEMPORARY', 'LOCAL TEMPORARY', 'ALIAS', 'SYNONYM', or a datasource specific type name.
# 4: remarks: A description of the table.

def fetch_schema(db_connection, db_name, db_schema):
    """Fetches schema metadata from database. Returns dict of table descriptors."""
    with db_connection() as cnxn:
        db_cursor = cnxn.cursor()
        table_descriptor_list = [z for z in db_cursor.tables(catalog=db_name, schema=db_schema)]
    
    table_type_dict = {}

    for descriptor in table_descriptor_list:        
        table_name = descriptor[2]
        table_type = descriptor[3]

        table_type_dict[table_name] = table_type

    return table_type_dict

#------------------------------------------------------------------------------
def fetch_schema_table(db_connection, db_name, db_schema):
    """Fetches metadata on schema and its tables from database. Returns dict of table and schema descriptors."""
    table_type_dict = fetch_schema(db_connection, db_name, db_schema)

    table_descriptor_dict = dict()

    for table_name, table_type in table_type_dict.items():
        table_descriptor_dict[table_name] = table_descriptor(
            table_type             = table_type,
            column_descriptor_dict = fetch_table(db_connection, db_name, db_schema, table_name)
        )

    return table_descriptor_dict

#------------------------------------------------------------------------------
def fetch_database_schema_table(db_connection, db_name, db_schema_list):
    """Fetches metadata on schema and its tables from database. Returns dict of schema+table descriptors."""

    schema_descriptor_dict = dict()

    for schema_name in db_schema_list:
        schema_descriptor_dict[schema_name] = fetch_schema_table(db_connection, db_name, schema_name)

    return schema_descriptor_dict

#------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------    
# 
#------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------ 
if __name__ == '__main__':

    db_name = 'srm_badges'
    db_connection = lambda : pyodbc.connect("DSN=ResearchData; Trusted_Connection=yes;")    

    #------------------------------------------------------------------------------        
    db_schemas = ['analysis', 'processed', 'data_definitions']    

    db_schema = 'analysis'
    db_table = 'cross_section'

    table_metadata    = fetch_table(db_connection, db_name, db_schema, db_table)
    schema_metadata   = fetch_schema_and_tables(db_connection, db_name, db_schema)
    database_metadata = fetch_database_schema_and_tables(db_connection, db_name, ['analysis', 'processed'])

    print('fetch_table')
    print(table_metadata)

    print('fetch_schema_and_tables')
    print(schema_metadata)

    print('fetch_database_schema_and_tables')
    print(database_metadata)
