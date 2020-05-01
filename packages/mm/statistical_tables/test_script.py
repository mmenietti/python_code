#------------------------------------------------------------
# Dependencies
#------------------------------------------------------------
import pathlib
import os
import argparse
import csv
import mm.data_utilities
import json

from dataclasses import dataclass, field
from typing import Tuple, Dict, List, Set

from docx import Document

from table_readers import read_regression_table_json
from object_model  import SxSRegressionTableParts
from string_model  import RegressionTableFormatting, create_sxs_regression_strings
from table_writers import write_sxs_regression_table_docx, DocxRegressionTableFormatting

from pkg_resources import resource_filename


#------------------------------------------------------------
# Entry Point
#------------------------------------------------------------
if __name__ == "__main__":
    
    # Read in table data
    file_paths = [resource_filename('mm.statistical_tables', 'test_input/test_regression_1.json'),
                 resource_filename('mm.statistical_tables', 'test_input/test_regression_2.json'),
                 resource_filename('mm.statistical_tables', 'test_input/test_regression_3.json'),
                 resource_filename('mm.statistical_tables', 'test_input/test_regression_4.json')]
    
    # Build the object model for the table
    #---------------------------------------------
    
    # Place table data into dict
    regression_summary_dict = {'model_' + str(k) : read_regression_table_json(pathlib.Path(x)) for k,x in enumerate(file_paths)}

    # Define the subset of coefficients to display in the table
    # the key is the `ugly' name better suited to scripting the table
    # the value is the `pretty` label for display in the table
    coefficient_labels = {
        "(Intercept)":'Constant',
        'migratedTRUE':'Migrated',
        'migrated_to_pakistanTRUE':'to Pakistan'
    }

    # Define the dependent variables to display in the table
    # the key is the `ugly' name better suited to scripting the table
    # the value is the `pretty` label for display in the table
    dependent_variable_labels = {
        'non_negative_view_on_partition':'non_negative_view_on_partition'
    }

    # Define the text to be placed at the bottom of the table
    notes = 'This is a note'

    # Choose the formatting to apply to the table.
    # The format is closely related to the output format.
    # e.g., The format may define the significance marker as `\star' 
    # if the output format is latex
    formatting = DocxRegressionTableFormatting()

    # Build the string model for the table
    #---------------------------------------------
    sxs_strings = create_sxs_regression_strings(
        regression_summary_dict=regression_summary_dict, 
        model_labels=None,
        dependent_variable_labels = dependent_variable_labels,
        coefficient_labels=coefficient_labels, 
        additional_feature_labels={'n':'N', 'r_sq':'Adj. R Sq.'}, 
        notes=notes,
        formatting=formatting        
    )
    
    # Write the table to the output file
    #---------------------------------------------
    base_docx_path = resource_filename('mm.statistical_tables', 'test_input/blank_document_o365_2020_04_28.docx')
    
    # Create docx based on the blank docx provided
    document = Document(base_docx_path)        

    # Write the table to the docx
    document = write_sxs_regression_table_docx(sxs_strings, document)

    # Save the docx to a new file
    document.save('test.docx')
